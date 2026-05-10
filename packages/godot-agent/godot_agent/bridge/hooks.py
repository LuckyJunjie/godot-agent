"""Agent hooks for game-generation requests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nanobot.agent.hook import AgentHook, AgentHookContext

if TYPE_CHECKING:
    from nanobot.agent.tools.registry import ToolRegistry


class GameGenerationHook(AgentHook):
    """Hook that intercepts game-generation requests and runs the planner."""

    def __init__(self, llm_client, tool_registry: "ToolRegistry") -> None:
        super().__init__(reraise=True)
        self.llm_client = llm_client
        self.tool_registry = tool_registry

    async def before_iteration(self, context: AgentHookContext) -> None:
        """Detect game-generation intent and inject a plan into context."""
        user_message = getattr(context, "user_message", "")
        if not user_message:
            return

        if not self._is_game_request(user_message):
            return

        from godot_agent.planner import GamePlanner
        from godot_agent.planner.executor import PhaseExecutor

        planner = GamePlanner(self.llm_client)
        try:
            plan = await planner.plan(user_message)
            executor = PhaseExecutor(self.tool_registry)
            results = await executor.execute_plan(plan)

            summary = self._format_results(results)
            # Inject as a system message so the LLM sees the plan results
            if hasattr(context, "inject_message"):
                context.inject_message({
                    "role": "system",
                    "content": summary,
                })
        except Exception as exc:
            # Don't block normal agent operation on planning failure
            if hasattr(context, "inject_message"):
                context.inject_message({
                    "role": "system",
                    "content": f"Game planning failed: {exc}",
                })

    @staticmethod
    def _is_game_request(message: str) -> bool:
        """Detect if a user message is a game-generation request."""
        lowered = message.lower()
        keywords = [
            "game", "make a ", "create a ", "build a ", "develop a ",
            "开发", "游戏", "做一款", "制作", "create game", "make game",
        ]
        return any(kw in lowered for kw in keywords)

    @staticmethod
    def _format_results(results) -> str:
        """Format phase execution results for the LLM context."""
        lines = ["=== Game Generation Results ==="]
        for r in results:
            status = "✅" if r.success else "❌"
            lines.append(f"{status} {r.phase_id}: {r.output[:200]}")
            if r.errors:
                for err in r.errors:
                    lines.append(f"   Error: {err}")
        return "\n".join(lines)
