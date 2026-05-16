"""Tests for bridge hooks."""

import pytest
from dataclasses import dataclass, field

from godot_agent.bridge.hooks import GameGenerationHook
from godot_agent.planner import GamePlanner, GamePlan
from nanobot.agent.tools.registry import ToolRegistry


@dataclass
class MockHookContext:
    """Mock AgentHookContext for testing."""
    iteration: int = 0
    messages: list[dict] = field(default_factory=list)
    user_message: str = ""
    injected: list[dict] = field(default_factory=list)

    def inject_message(self, msg: dict) -> None:
        self.injected.append(msg)


class MockLLM:
    """Mock LLM that returns a simple plan."""

    def __init__(self, response: str = None):
        self.response = response or '{"genre": "arcade", "phases": []}'

    async def chat(self, messages):
        return self.response


class TestGameGenerationHook:
    async def test_detects_game_request(self):
        hook = GameGenerationHook(MockLLM(), ToolRegistry())
        assert hook._is_game_request("make a game") is True
        assert hook._is_game_request("create a platformer") is True
        assert hook._is_game_request("build a snake game") is True
        assert hook._is_game_request("开发游戏") is True
        assert hook._is_game_request("做一款射击游戏") is True

    async def test_ignores_non_game_request(self):
        hook = GameGenerationHook(MockLLM(), ToolRegistry())
        assert hook._is_game_request("hello world") is False
        assert hook._is_game_request("fix this bug") is False
        assert hook._is_game_request("refactor code") is False

    async def test_before_iteration_runs_planner(self, temp_project, monkeypatch):
        import os
        monkeypatch.chdir(temp_project)
        llm = MockLLM('{"genre": "puzzle", "phases": []}')
        registry = ToolRegistry()
        hook = GameGenerationHook(llm, registry)

        ctx = MockHookContext(user_message="make a puzzle game")
        await hook.before_iteration(ctx)

        assert len(ctx.injected) == 1
        assert ctx.injected[0]["role"] == "system"
        assert "Game Generation Results" in ctx.injected[0]["content"]

    async def test_before_iteration_skips_non_game(self, temp_project, monkeypatch):
        import os
        monkeypatch.chdir(temp_project)
        llm = MockLLM()
        registry = ToolRegistry()
        hook = GameGenerationHook(llm, registry)

        ctx = MockHookContext(user_message="hello there")
        await hook.before_iteration(ctx)

        assert len(ctx.injected) == 0

    async def test_before_iteration_empty_message(self):
        hook = GameGenerationHook(MockLLM(), ToolRegistry())
        ctx = MockHookContext(user_message="")
        await hook.before_iteration(ctx)
        assert len(ctx.injected) == 0

    async def test_format_results(self):
        from godot_agent.planner.executor import PhaseResult

        results = [
            PhaseResult(phase_id="design", success=True, output="ok", errors=[]),
            PhaseResult(phase_id="build", success=False, output="", errors=["failed"]),
        ]
        formatted = GameGenerationHook._format_results(results)
        assert "✅ design" in formatted
        assert "❌ build" in formatted
        assert "failed" in formatted

    async def test_plan_failure_reported(self, temp_project, monkeypatch):
        import os
        monkeypatch.chdir(temp_project)

        class BadLLM:
            async def chat(self, messages):
                raise ValueError("API down")

        hook = GameGenerationHook(BadLLM(), ToolRegistry())
        ctx = MockHookContext(user_message="make a game")
        await hook.before_iteration(ctx)

        assert len(ctx.injected) == 1
        assert "Game planning failed" in ctx.injected[0]["content"]
