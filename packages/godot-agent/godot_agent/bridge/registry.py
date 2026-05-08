"""Register Godot Agent tools into a nanobot ToolRegistry."""

from typing import TYPE_CHECKING

from godot_agent.bridge.tools import (
    SceneInspectTool,
    SceneEditTool,
    GDDReadTool,
    GDDValidateTool,
    AssetGenerateTool,
    HarnessRunTool,
)

if TYPE_CHECKING:
    from nanobot.agent.tools.registry import ToolRegistry


GODOT_TOOLS = [
    SceneInspectTool,
    SceneEditTool,
    GDDReadTool,
    GDDValidateTool,
    AssetGenerateTool,
    HarnessRunTool,
]


def register_godot_tools(registry: "ToolRegistry") -> None:
    """Register all Godot Agent tools into a nanobot ToolRegistry."""
    for tool_cls in GODOT_TOOLS:
        registry.register(tool_cls())
