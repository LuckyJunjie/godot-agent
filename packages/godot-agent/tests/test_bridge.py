"""Tests for godot_agent.bridge nanobot integration."""

import pytest

from godot_agent.bridge import (
    SceneInspectTool,
    SceneEditTool,
    GDDReadTool,
    GDDValidateTool,
    AssetGenerateTool,
    HarnessRunTool,
    register_godot_tools,
)


class TestToolSpecs:
    def test_scene_inspect_name(self):
        t = SceneInspectTool()
        assert t.name == "gd_scene_inspect"
        assert t.read_only is True

    def test_scene_edit_name(self):
        t = SceneEditTool()
        assert t.name == "gd_scene_edit"

    def test_gdd_read_name(self):
        t = GDDReadTool()
        assert t.name == "gd_gdd_read"
        assert t.read_only is True

    def test_gdd_validate_name(self):
        t = GDDValidateTool()
        assert t.name == "gd_gdd_validate"
        assert t.read_only is True

    def test_asset_generate_name(self):
        t = AssetGenerateTool()
        assert t.name == "gd_asset_generate"

    def test_harness_run_name(self):
        t = HarnessRunTool()
        assert t.name == "gd_harness_run"


class TestToolSchemas:
    def test_scene_inspect_schema(self):
        t = SceneInspectTool()
        schema = t.to_schema()
        assert schema["function"]["name"] == "gd_scene_inspect"
        assert "path" in schema["function"]["parameters"]["properties"]

    def test_scene_edit_schema(self):
        t = SceneEditTool()
        schema = t.to_schema()
        assert schema["function"]["name"] == "gd_scene_edit"
        assert "action" in schema["function"]["parameters"]["properties"]


class TestRegisterGodotTools:
    def test_registration(self):
        from nanobot.agent.tools.registry import ToolRegistry

        registry = ToolRegistry()
        register_godot_tools(registry)

        assert registry.has("gd_scene_inspect")
        assert registry.has("gd_scene_edit")
        assert registry.has("gd_gdd_read")
        assert registry.has("gd_gdd_validate")
        assert registry.has("gd_asset_generate")
        assert registry.has("gd_harness_run")

    def test_definitions_present(self):
        from nanobot.agent.tools.registry import ToolRegistry

        registry = ToolRegistry()
        register_godot_tools(registry)
        defs = registry.get_definitions()
        names = [d["function"]["name"] for d in defs]
        assert "gd_scene_inspect" in names
        assert "gd_gdd_read" in names
