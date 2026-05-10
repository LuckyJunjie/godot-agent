"""Dynamic nanobot Tool wrappers for godogen YAML skills."""

from __future__ import annotations

from typing import Any

from nanobot.agent.tools.base import Tool

from godot_agent.godogen import GodogenIntegrator, ToolSpec


class GodogenSkillTool(Tool):
    """A nanobot Tool backed by a godogen YAML skill."""

    def __init__(self, spec: ToolSpec, integrator: GodogenIntegrator):
        self._spec = spec
        self._integrator = integrator

    @property
    def name(self) -> str:
        return f"godogen_{self._spec.name}"

    @property
    def description(self) -> str:
        return (
            f"Godogen skill: {self._spec.name}\n"
            f"{self._spec.description}\n"
            f"Renders a Jinja2 template into GDScript, scene, or config code."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        schema = self._spec.input_schema or {"type": "object", "properties": {}}
        # Ensure all godogen parameters are required by default
        if "required" not in schema:
            schema["required"] = list(schema.get("properties", {}).keys())
        return schema

    async def execute(self, **kwargs) -> str:
        rendered = self._integrator.render_skill(self._spec.name, kwargs)
        if not rendered:
            return f"Error: skill '{self._spec.name}' returned empty output"
        return rendered
