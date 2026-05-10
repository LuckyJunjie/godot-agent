"""GDD creation tool for the agent bridge."""

from __future__ import annotations

from typing import Any

from nanobot.agent.tools.base import Tool

from godot_agent.gdd import GDDEngine


class GDDCreateTool(Tool):
    """Create or initialize a Game Design Document."""

    @property
    def name(self) -> str:
        return "gd_gdd_create"

    @property
    def description(self) -> str:
        return (
            "Initialize a GDD directory structure and create a story. "
            "If the GDD already exists, adds a new story to it."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_root": {"type": "string", "default": "."},
                "story_id": {"type": "string", "default": "001"},
                "title": {"type": "string", "description": "Story title"},
                "content": {"type": "string", "description": "Story description / narrative"},
                "scenes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                    "description": "List of scene file paths this story requires",
                },
                "scripts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                    "description": "List of script file paths this story requires",
                },
                "tests": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                    "description": "List of test file paths this story requires",
                },
                "acceptance": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                    "description": "Acceptance criteria for this story",
                },
            },
            "required": ["title"],
        }

    async def execute(
        self,
        project_root: str = ".",
        story_id: str = "001",
        title: str = "",
        content: str = "",
        scenes: list[str] | None = None,
        scripts: list[str] | None = None,
        tests: list[str] | None = None,
        acceptance: list[str] | None = None,
    ) -> str:
        engine = GDDEngine(project_root)
        engine.initialize()

        story = engine.create_story(
            story_id=story_id,
            title=title,
            content=content,
        )

        # Update with references
        story.scenes = scenes or []
        story.scripts = scripts or []
        story.tests = tests or []
        story.acceptance = acceptance or []
        story.status = "approved"

        engine.update_story(
            story_id,
            scenes=story.scenes,
            scripts=story.scripts,
            tests=story.tests,
            acceptance=story.acceptance,
            status="approved",
        )

        index_path = engine.gdd_dir / "index.md"
        return (
            f"Created GDD story '{title}' (ID: {story_id})\n"
            f"  Scenes: {len(story.scenes)}\n"
            f"  Scripts: {len(story.scripts)}\n"
            f"  Tests: {len(story.tests)}\n"
            f"  Index: {index_path}"
        )
