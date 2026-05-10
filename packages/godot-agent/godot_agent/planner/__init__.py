"""GamePlanner — LLM-driven decomposition of game requirements into executable phases."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from godot_agent.state import GameProjectState


@dataclass
class Phase:
    """A single phase of game generation."""

    id: str
    name: str
    description: str
    tool: str  # e.g., "gd_create_component", "gd_asset_generate"
    parameters: dict = field(default_factory=dict)
    prerequisites: list[str] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)
    max_retries: int = 3


@dataclass
class GamePlan:
    """A complete plan for generating a game."""

    requirement: str
    genre: str
    phases: list[Phase] = field(default_factory=list)
    current_phase_index: int = 0


class GamePlanner:
    """Uses LLM to decompose a requirement into a GamePlan."""

    PLAN_PROMPT = """You are a game architect. Decompose the following game requirement into a structured implementation plan.

Requirement: {requirement}

Return a JSON object with this structure:
{{
  "genre": "snake|platformer|puzzle|shooter|rpg|arcade",
  "phases": [
    {{
      "id": "design_gdd",
      "name": "Design GDD",
      "description": "Create game design document",
      "tool": "gd_gdd_create",
      "parameters": {{"story_id": "001", "title": "..."}},
      "prerequisites": [],
      "acceptance": ["GDD index.md exists", "At least one story defined"],
      "max_retries": 3
    }},
    {{
      "id": "scaffold_player",
      "name": "Create Player Component",
      "description": "Create player scene and script",
      "tool": "gd_create_component",
      "parameters": {{
        "component_type": "player",
        "name": "Player",
        "behaviors": ["movement", "collision", "input"]
      }},
      "prerequisites": ["design_gdd"],
      "acceptance": ["scenes/player.tscn exists", "scripts/player.gd exists"],
      "max_retries": 3
    }}
  ]
}}

Rules:
- Phases must be ordered by dependency (prerequisites reference earlier phase IDs).
- Use only these tools: gd_gdd_create, gd_gdd_read, gd_gdd_validate, gd_create_component, gd_asset_generate, gd_scene_edit, gd_harness_run, gd_project_inspect, godogen_*, write_file, edit_file.
- Include at minimum: design, scaffold (player + core mechanics), assets, validate.
- Keep phases small and testable (1–2 files per phase).
- Only return valid JSON, no markdown code blocks.
"""

    def __init__(self, llm_client):
        self.llm = llm_client

    async def plan(self, requirement: str, project_root: str = ".") -> GamePlan:
        """Generate a GamePlan from a natural language requirement."""
        from godot_agent.state import GameProjectState

        # Check for existing state to resume
        state = GameProjectState.load(project_root)
        if state and state.current_phase not in ("idle", "complete"):
            return self._resume_from_state(state)

        prompt = self.PLAN_PROMPT.format(requirement=requirement)
        response = await self.llm.chat([{"role": "user", "content": prompt}])

        # Robust JSON extraction
        data = self._extract_json(response)
        if not data:
            raise ValueError(f"LLM did not return valid JSON plan. Response:\n{response}")

        phases = [Phase(**p) for p in data.get("phases", [])]
        plan = GamePlan(
            requirement=requirement,
            genre=data.get("genre", "generic"),
            phases=phases,
        )

        # Save initial state
        state = GameProjectState(
            requirement=requirement,
            project_root=project_root,
            genre=plan.genre,
            current_phase="designing",
            pending_phases=[p.id for p in phases],
            gdd_path=str(Path(project_root) / "gdd" / "index.md"),
        )
        state.save()
        return plan

    def _resume_from_state(self, state: "GameProjectState") -> GamePlan:
        """Resume a plan from persisted state."""
        # Reconstruct a minimal plan from state
        # In a full implementation, we'd persist the full plan JSON
        return GamePlan(
            requirement=state.requirement,
            genre=state.genre,
            phases=[],  # Would be loaded from persisted plan
            current_phase_index=len(state.completed_phases),
        )

    @staticmethod
    def _extract_json(response: str) -> Optional[dict]:
        """Extract JSON from LLM response, handling markdown blocks."""
        text = response.strip()

        # Try to find JSON in markdown code block
        if "```json" in text:
            start = text.find("```json") + len("```json")
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
