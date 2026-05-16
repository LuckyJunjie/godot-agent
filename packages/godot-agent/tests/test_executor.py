"""Tests for planner/executor.py async execution paths."""

import pytest
from pathlib import Path

from godot_agent.planner import Phase, GamePlan
from godot_agent.planner.executor import PhaseExecutor, PhaseResult


class MockTool:
    """Mock tool for testing."""

    def __init__(self, result: str = "ok", fail: bool = False):
        self.result = result
        self.fail = fail

    async def execute(self, **kwargs):
        if self.fail:
            raise RuntimeError("Tool failed")
        return self.result


class MockRegistry:
    """Mock tool registry."""

    def __init__(self, tools: dict = None):
        self._tools = tools or {}

    def get(self, name: str):
        return self._tools.get(name)


class TestPhaseExecutor:
    async def test_execute_plan_all_success(self, temp_project):
        registry = MockRegistry({
            "gd_gdd_create": MockTool("Created GDD"),
            "gd_create_component": MockTool("Created player"),
        })
        executor = PhaseExecutor(registry)

        plan = GamePlan(
            requirement="make a game",
            genre="arcade",
            phases=[
                Phase(id="design", name="Design", description="", tool="gd_gdd_create", parameters={}),
                Phase(id="player", name="Player", description="", tool="gd_create_component", parameters={}),
            ],
        )

        results = await executor.execute_plan(plan)
        assert len(results) == 2
        assert all(r.success for r in results)
        assert executor.completed_phases == {"design", "player"}

    async def test_execute_plan_prerequisite_not_met(self, temp_project):
        registry = MockRegistry({
            "gd_create_component": MockTool("Created player"),
        })
        executor = PhaseExecutor(registry)

        plan = GamePlan(
            requirement="make a game",
            genre="arcade",
            phases=[
                Phase(id="player", name="Player", description="", tool="gd_create_component", prerequisites=["design"]),
            ],
        )

        results = await executor.execute_plan(plan)
        assert len(results) == 1
        assert results[0].success is False
        assert "Prerequisites not met" in results[0].errors[0]

    async def test_execute_plan_tool_not_found(self, temp_project):
        registry = MockRegistry({})
        executor = PhaseExecutor(registry)

        plan = GamePlan(
            requirement="make a game",
            genre="arcade",
            phases=[
                Phase(id="design", name="Design", description="", tool="missing_tool"),
            ],
        )

        results = await executor.execute_plan(plan)
        assert len(results) == 1
        assert results[0].success is False
        assert "not found" in results[0].errors[0]

    async def test_execute_plan_stops_on_failure(self, temp_project):
        registry = MockRegistry({
            "fail_tool": MockTool(fail=True),
            "success_tool": MockTool("ok"),
        })
        executor = PhaseExecutor(registry)

        plan = GamePlan(
            requirement="make a game",
            genre="arcade",
            phases=[
                Phase(id="first", name="First", description="", tool="fail_tool"),
                Phase(id="second", name="Second", description="", tool="success_tool"),
            ],
        )

        results = await executor.execute_plan(plan)
        assert len(results) == 1  # Stops after first failure
        assert results[0].success is False
        assert "Tool failed" in results[0].errors[0]

    async def test_execute_plan_with_retries_then_success(self, temp_project):
        """Test that a phase can succeed after retries."""
        call_count = 0

        class FlakyTool:
            async def execute(self, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    raise RuntimeError("Flaky")
                return "Fixed"

        registry = MockRegistry({"flaky": FlakyTool()})
        executor = PhaseExecutor(registry)

        plan = GamePlan(
            requirement="make a game",
            genre="arcade",
            phases=[
                Phase(id="flaky", name="Flaky", description="", tool="flaky", max_retries=3),
            ],
        )

        results = await executor.execute_plan(plan)
        assert results[0].success is True
        assert results[0].retry_count == 1

    async def test_acceptance_file_exists(self, temp_project):
        existing = temp_project / "player.tscn"
        existing.write_text("scene", encoding="utf-8")

        phase = Phase(
            id="test",
            name="Test",
            description="",
            tool="t",
            acceptance=[f"{existing} exists"],
        )
        errors = PhaseExecutor._check_acceptance(phase, "output")
        assert len(errors) == 0

    async def test_acceptance_file_missing(self, temp_project):
        missing = temp_project / "missing.tscn"

        phase = Phase(
            id="test",
            name="Test",
            description="",
            tool="t",
            acceptance=[f"{missing} exists"],
        )
        errors = PhaseExecutor._check_acceptance(phase, "output")
        assert len(errors) == 1

    async def test_find_file_path(self):
        phase = Phase(
            id="test",
            name="Test",
            description="",
            tool="t",
            parameters={"path": "/some/script.gd"},
        )
        assert PhaseExecutor._find_file_path(phase) == "/some/script.gd"

    async def test_find_file_path_no_match(self):
        phase = Phase(
            id="test",
            name="Test",
            description="",
            tool="t",
            parameters={"other": "value"},
        )
        assert PhaseExecutor._find_file_path(phase) is None

    async def test_topological_sort_complex(self):
        phases = [
            Phase(id="c", name="C", description="", tool="t", prerequisites=["a", "b"]),
            Phase(id="a", name="A", description="", tool="t", prerequisites=[]),
            Phase(id="b", name="B", description="", tool="t", prerequisites=["a"]),
            Phase(id="d", name="D", description="", tool="t", prerequisites=["c"]),
        ]
        sorted_phases = PhaseExecutor._topological_sort(phases)
        ids = [p.id for p in sorted_phases]
        assert ids.index("a") < ids.index("b")
        assert ids.index("a") < ids.index("c")
        assert ids.index("b") < ids.index("c")
        assert ids.index("c") < ids.index("d")
