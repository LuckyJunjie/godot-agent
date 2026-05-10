"""Tests for GamePlanner and PhaseExecutor."""

import pytest
from pathlib import Path

from godot_agent.planner import GamePlanner, GamePlan, Phase
from godot_agent.planner.executor import PhaseExecutor


class MockLLM:
    """Mock LLM client for testing."""

    def __init__(self, response: str = None):
        self.response = response or '{"genre": "snake", "phases": []}'

    async def chat(self, messages):
        return self.response


class TestGamePlanner:
    async def test_plan_extracts_json_from_markdown(self, temp_project):
        llm = MockLLM('''```json
{"genre": "platformer", "phases": [
  {"id": "design", "name": "Design", "description": "Design GDD", "tool": "gd_gdd_create", "parameters": {"title": "Test"}, "prerequisites": [], "acceptance": ["GDD exists"], "max_retries": 3}
]}
```''')
        planner = GamePlanner(llm)
        plan = await planner.plan("Make a platformer", str(temp_project))
        assert plan.genre == "platformer"
        assert len(plan.phases) == 1
        assert plan.phases[0].id == "design"

    async def test_plan_extracts_plain_json(self, temp_project):
        llm = MockLLM('{"genre": "puzzle", "phases": []}')
        planner = GamePlanner(llm)
        plan = await planner.plan("Make a puzzle game", str(temp_project))
        assert plan.genre == "puzzle"
        assert len(plan.phases) == 0

    async def test_plan_invalid_json_raises(self, temp_project):
        llm = MockLLM("not json")
        planner = GamePlanner(llm)
        with pytest.raises(ValueError):
            await planner.plan("Make a game", str(temp_project))


class TestPhaseExecutor:
    def test_topological_sort(self):
        phases = [
            Phase(id="b", name="B", description="", tool="t", prerequisites=["a"]),
            Phase(id="a", name="A", description="", tool="t", prerequisites=[]),
            Phase(id="c", name="C", description="", tool="t", prerequisites=["b"]),
        ]
        sorted_phases = PhaseExecutor._topological_sort(phases)
        ids = [p.id for p in sorted_phases]
        assert ids.index("a") < ids.index("b")
        assert ids.index("b") < ids.index("c")

    def test_prerequisites_met(self):
        executor = PhaseExecutor(None)
        executor.completed_phases = {"a", "b"}
        phase = Phase(id="c", name="C", description="", tool="t", prerequisites=["a", "b"])
        assert executor._prerequisites_met(phase)

        phase2 = Phase(id="d", name="D", description="", tool="t", prerequisites=["a", "z"])
        assert not executor._prerequisites_met(phase2)

    def test_check_acceptance_file_exists(self, tmp_path):
        phase = Phase(
            id="test",
            name="Test",
            description="",
            tool="t",
            acceptance=[f"{tmp_path / 'exists.txt'} exists"],
        )
        (tmp_path / "exists.txt").write_text("ok")
        errors = PhaseExecutor._check_acceptance(phase, "some output")
        assert len(errors) == 0

    def test_check_acceptance_file_missing(self, tmp_path):
        phase = Phase(
            id="test",
            name="Test",
            description="",
            tool="t",
            acceptance=[f"{tmp_path / 'missing.txt'} exists"],
        )
        errors = PhaseExecutor._check_acceptance(phase, "some output")
        assert len(errors) == 1
