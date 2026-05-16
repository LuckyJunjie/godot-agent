"""Tests for SceneInspectTool improvements."""

import pytest
from pathlib import Path

from godot_agent.bridge.tools import SceneInspectTool


class TestSceneInspectTool:
    async def test_inspects_node_tree(self, temp_project, sample_tscn):
        scene_file = temp_project / "main.tscn"
        scene_file.write_text(sample_tscn, encoding="utf-8")

        tool = SceneInspectTool()
        result = await tool.execute(path=str(scene_file))

        assert "Scene:" in result
        assert "External resources: 1" in result
        assert "Root: Main (Node2D)" in result
        assert "Player (CharacterBody2D)" in result

    async def test_missing_scene(self, temp_project):
        tool = SceneInspectTool()
        result = await tool.execute(path=str(temp_project / "missing.tscn"))
        assert "Error:" in result
