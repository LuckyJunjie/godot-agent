"""Godot Agent tools wrapped as nanobot Tool subclasses."""

from typing import Any
from pathlib import Path

from nanobot.agent.tools.base import Tool

from godot_agent.scene import SceneDocument
from godot_agent.gdd import GDDEngine
from godot_agent.assets import AssetPipeline, ImageMeta, AudioMeta, ModelMeta
from godot_agent.harness import HarnessRunner


class SceneInspectTool(Tool):
    """Inspect a Godot scene file (.tscn)."""

    @property
    def name(self) -> str:
        return "gd_scene_inspect"

    @property
    def description(self) -> str:
        return "Inspect a Godot scene file and return node tree information."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or res:// path to the .tscn file"
                }
            },
            "required": ["path"]
        }

    @property
    def read_only(self) -> bool:
        return True

    async def execute(self, path: str) -> str:
        doc = SceneDocument()
        doc.load(path)
        lines = [f"Scene: {path}", f"External resources: {len(doc.ext_resources)}"]
        return "\n".join(lines)


class SceneEditTool(Tool):
    """Edit a Godot scene file."""

    @property
    def name(self) -> str:
        return "gd_scene_edit"

    @property
    def description(self) -> str:
        return "Edit a Godot scene: add/remove nodes, set properties, connect signals."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "action": {
                    "type": "string",
                    "enum": ["add_node", "remove_node", "set_property", "connect_signal"]
                },
                "node_path": {"type": "string"},
                "node_type": {"type": "string"},
                "property": {"type": "string"},
                "value": {"type": "string"},
                "signal": {"type": "string"},
                "target_path": {"type": "string"},
                "target_method": {"type": "string"}
            },
            "required": ["path", "action"]
        }

    async def execute(self, **kwargs) -> str:
        path = kwargs["path"]
        action = kwargs["action"]
        doc = SceneDocument()
        doc.load(path)

        if action == "add_node":
            parent = kwargs.get("node_path", ".")
            name = kwargs.get("property", "NewNode")
            node_type = kwargs.get("node_type", "Node")
            doc.add_node(parent, name, node_type)
            doc.save(path)
            return f"Added node {name} ({node_type}) to {parent}"

        return f"Action {action} not yet fully implemented"


class GDDReadTool(Tool):
    """Read stories from the Game Design Document."""

    @property
    def name(self) -> str:
        return "gd_gdd_read"

    @property
    def description(self) -> str:
        return "Read GDD stories, mechanics, or style guide."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_root": {"type": "string", "default": "."},
                "story_id": {"type": "string"},
                "section": {"type": "string", "enum": ["stories", "mechanics", "assets", "index"]}
            },
            "required": ["project_root"]
        }

    @property
    def read_only(self) -> bool:
        return True

    async def execute(self, project_root: str = ".", story_id: str = "", section: str = "index") -> str:
        engine = GDDEngine(project_root)
        if story_id:
            stories = engine.load_stories()
            for story in stories:
                if story.id == story_id:
                    return engine._story_to_markdown(story)
            return f"Story {story_id} not found"
        # Return index
        index = engine.gdd_dir / "index.md"
        if index.exists():
            return index.read_text()
        return "No GDD index found"


class GDDValidateTool(Tool):
    """Validate GDD traceability."""

    @property
    def name(self) -> str:
        return "gd_gdd_validate"

    @property
    def description(self) -> str:
        return "Validate that all GDD-referenced scenes, scripts, and tests exist."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_root": {"type": "string", "default": "."}
            }
        }

    @property
    def read_only(self) -> bool:
        return True

    async def execute(self, project_root: str = ".") -> str:
        engine = GDDEngine(project_root)
        result = engine.validate_traceability()
        if result["valid"]:
            return "GDD traceability: all references valid"
        return "GDD issues:\n" + "\n".join(result["issues"])


class AssetGenerateTool(Tool):
    """Generate a game asset via LLM API."""

    @property
    def name(self) -> str:
        return "gd_asset_generate"

    @property
    def description(self) -> str:
        return "Generate an image, audio, or 3D model asset for the game."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_root": {"type": "string", "default": "."},
                "asset_type": {"type": "string", "enum": ["image", "audio", "model"]},
                "name": {"type": "string"},
                "prompt": {"type": "string"},
                "resolution": {"type": "string", "default": "256x256"},
                "duration": {"type": "number", "default": 3.0}
            },
            "required": ["asset_type", "name", "prompt"]
        }

    async def execute(self, project_root: str = ".", asset_type: str = "image", name: str = "", prompt: str = "", resolution: str = "256x256", duration: float = 3.0) -> str:
        pipeline = AssetPipeline(project_root)
        pipeline.initialize()

        if asset_type == "image":
            w, h = map(int, resolution.split("x"))
            meta = ImageMeta(prompt=prompt, resolution=(w, h))
            path = await pipeline.generate_image(meta, name)
            return f"Generated image: {path}"
        elif asset_type == "audio":
            meta = AudioMeta(prompt=prompt, duration=int(duration))
            path = await pipeline.generate_audio(meta, name)
            return f"Generated audio: {path}"
        else:
            return f"Asset type {asset_type} generation stub"


class HarnessRunTool(Tool):
    """Run Godot test harness."""

    @property
    def name(self) -> str:
        return "gd_harness_run"

    @property
    def description(self) -> str:
        return "Run a GDScript unit test or scene integration test headlessly."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_root": {"type": "string", "default": "."},
                "test_script": {"type": "string"},
                "scene_path": {"type": "string"}
            }
        }

    async def execute(self, project_root: str = ".", test_script: str = "", scene_path: str = "") -> str:
        runner = HarnessRunner(project_root)
        if test_script:
            result = await runner.run_unit(test_script)
            status = "PASSED" if result.passed else "FAILED"
            return f"Test {status}: {result.message}"
        elif scene_path:
            result = await runner.run_scene(scene_path)
            status = "LOADED" if result.loaded else "FAILED"
            return f"Scene {status}: {result.scene_path}"
        return "Specify test_script or scene_path"
