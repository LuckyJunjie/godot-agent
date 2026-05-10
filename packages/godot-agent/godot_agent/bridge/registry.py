"""Register Godot Agent tools into a nanobot ToolRegistry."""

from pathlib import Path
from typing import TYPE_CHECKING

from godot_agent.bridge.tools import (
    SceneInspectTool,
    SceneEditTool,
    GDDReadTool,
    GDDValidateTool,
    AssetGenerateTool,
    HarnessRunTool,
)
from godot_agent.bridge.tools_gdd import GDDCreateTool
from godot_agent.bridge.tools_compound import (
    CreateComponentTool,
    CreateGameFromGDDTool,
)
from godot_agent.bridge.tools_godogen import GodogenSkillTool
from godot_agent.bridge.tools_lsp import GDScriptLintTool, GDScriptGotoDefTool
from godot_agent.bridge.tools_missing import (
    CreateScriptTool,
    SetInputActionTool,
    ProjectInspectTool,
    ExportGameTool,
)
from godot_agent.godogen import GodogenIntegrator

if TYPE_CHECKING:
    from nanobot.agent.tools.registry import ToolRegistry


GODOT_TOOLS = [
    SceneInspectTool,
    SceneEditTool,
    GDDReadTool,
    GDDValidateTool,
    AssetGenerateTool,
    HarnessRunTool,
    GDDCreateTool,
    # Compound tools
    CreateComponentTool,
    CreateGameFromGDDTool,
    # LSP tools
    GDScriptLintTool,
    GDScriptGotoDefTool,
    # Missing tools
    CreateScriptTool,
    SetInputActionTool,
    ProjectInspectTool,
    ExportGameTool,
]


def register_godot_tools(registry: "ToolRegistry") -> None:
    """Register all Godot Agent tools + dynamic godogen skills into a nanobot ToolRegistry."""
    # Register static tools
    for tool_cls in GODOT_TOOLS:
        registry.register(tool_cls())

    # Auto-discover and register godogen skills
    # Locate skills relative to the godot_agent package
    from godot_agent import __file__ as _ga_file
    _ga_dir = Path(_ga_file).parent
    skills_root = _ga_dir.parent  # packages/godot-agent/
    integrator = GodogenIntegrator(str(skills_root))
    integrator.load_all()
    for tool_spec in integrator.tools:
        registry.register(GodogenSkillTool(tool_spec, integrator))
