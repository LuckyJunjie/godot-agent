"""PhaseExecutor — Runs phases from a GamePlan, handling prerequisites and retries."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from godot_agent.planner import GamePlan, Phase
    from godot_agent.planner.fix_loop import FixLoop


@dataclass
class PhaseResult:
    phase_id: str
    success: bool
    output: str
    errors: list[str] = field(default_factory=list)
    retry_count: int = 0


class PhaseExecutor:
    """Executes a GamePlan phase by phase, with validation and retry logic."""

    def __init__(
        self,
        registry,
        state_path: Optional[str] = None,
        fix_loop: Optional["FixLoop"] = None,
    ):
        from nanobot.agent.tools.registry import ToolRegistry

        self.registry: ToolRegistry = registry
        self.state_path = state_path
        self.fix_loop = fix_loop
        self.completed_phases: set[str] = set()
        self.results: list[PhaseResult] = []

    async def execute_plan(self, plan: "GamePlan") -> list[PhaseResult]:
        """Execute all phases in dependency order."""
        sorted_phases = self._topological_sort(plan.phases)

        for phase in sorted_phases:
            if not self._prerequisites_met(phase):
                self.results.append(
                    PhaseResult(
                        phase_id=phase.id,
                        success=False,
                        output="",
                        errors=[f"Prerequisites not met: {phase.prerequisites}"],
                        retry_count=0,
                    )
                )
                continue

            result = await self._execute_phase_with_retries(phase)
            self.results.append(result)

            if result.success:
                self.completed_phases.add(phase.id)
                # Update persistent state
                self._update_state(phase.id, success=True)
            else:
                self._update_state(phase.id, success=False, errors=result.errors)
                # Stop on first unrecoverable failure
                break

        return self.results

    async def _execute_phase_with_retries(self, phase: "Phase") -> PhaseResult:
        """Execute a single phase with retry logic."""
        tool = self.registry.get(phase.tool)
        if not tool:
            return PhaseResult(
                phase_id=phase.id,
                success=False,
                output="",
                errors=[f"Tool '{phase.tool}' not found in registry"],
                retry_count=0,
            )

        errors = []
        for attempt in range(phase.max_retries):
            try:
                output = await tool.execute(**phase.parameters)
            except Exception as exc:
                output = f"Tool execution error: {exc}"
                errors = [str(exc)]
                continue  # Retry on exception

            # Run acceptance checks
            errors = self._check_acceptance(phase, output)

            if not errors:
                return PhaseResult(
                    phase_id=phase.id,
                    success=True,
                    output=output,
                    errors=[],
                    retry_count=attempt,
                )

            # Try FixLoop if we have a file path and fix_loop is available
            file_path = self._find_file_path(phase)
            if file_path and self.fix_loop:
                fixed, _ = await self.fix_loop.fix(file_path, errors)
                if fixed:
                    return PhaseResult(
                        phase_id=phase.id,
                        success=True,
                        output=f"Fixed after {attempt + 1} attempt(s)",
                        errors=[],
                        retry_count=attempt,
                    )

        return PhaseResult(
            phase_id=phase.id,
            success=False,
            output="",
            errors=errors,
            retry_count=phase.max_retries,
        )

    def _prerequisites_met(self, phase: "Phase") -> bool:
        return all(p in self.completed_phases for p in phase.prerequisites)

    @staticmethod
    def _check_acceptance(phase: "Phase", output: str) -> list[str]:
        """Check if phase output meets acceptance criteria."""
        errors = []
        for criterion in phase.acceptance:
            lowered = criterion.lower()
            # File existence check: "<path> exists" or "<path> was created"
            if lowered.endswith(" exists") or lowered.endswith(" was created"):
                # Extract path from criterion like "scenes/player.tscn exists"
                parts = criterion.rsplit(" ", 1)
                path = parts[0]
                if not Path(path).exists():
                    errors.append(f"Acceptance criterion not met: {criterion}")
            elif lowered not in output.lower():
                errors.append(f"Acceptance criterion not met: {criterion}")
        return errors

    @staticmethod
    def _find_file_path(phase: "Phase") -> Optional[str]:
        """Try to find a file path in phase parameters for FixLoop."""
        for key in ("path", "script_path", "scene_path", "project_root"):
            if key in phase.parameters:
                val = phase.parameters[key]
                if isinstance(val, str) and val.endswith(".gd"):
                    return val
        return None

    def _update_state(self, phase_id: str, success: bool, errors: Optional[list[str]] = None) -> None:
        from godot_agent.state import GameProjectState

        if not self.state_path:
            return
        state = GameProjectState.load(self.state_path)
        if state:
            if success:
                state.mark_phase_complete(phase_id)
            else:
                for err in (errors or []):
                    state.add_issue(phase_id, err, severity="error")

    @staticmethod
    def _topological_sort(phases: list["Phase"]) -> list["Phase"]:
        """Sort phases so prerequisites come before dependents."""
        phase_map = {p.id: p for p in phases}
        in_degree = {p.id: len(p.prerequisites) for p in phases}
        queue = [p for p in phases if in_degree[p.id] == 0]
        sorted_phases: list["Phase"] = []

        while queue:
            phase = queue.pop(0)
            sorted_phases.append(phase)
            for other in phases:
                if phase.id in other.prerequisites:
                    in_degree[other.id] -= 1
                    if in_degree[other.id] == 0:
                        queue.append(other)

        # Append any remaining (cycle or missing prerequisites)
        for p in phases:
            if p not in sorted_phases:
                sorted_phases.append(p)

        return sorted_phases
