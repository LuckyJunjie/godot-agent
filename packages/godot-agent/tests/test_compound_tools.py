"""Tests for compound bridge tools."""

import pytest
from pathlib import Path

from godot_agent.bridge.tools_compound import CreateComponentTool
from godot_agent.bridge.tools_missing import CreateScriptTool, SetInputActionTool, ProjectInspectTool


class TestCreateComponentTool:
    async def test_create_player_component(self, temp_project):
        tool = CreateComponentTool()
        result = await tool.execute(
            project_root=str(temp_project),
            component_type="player",
            name="Player",
            behaviors=["movement", "collision"],
            extends="CharacterBody2D",
        )
        assert "Created component 'Player'" in result
        assert (temp_project / "scripts" / "player.gd").exists()
        assert (temp_project / "scenes" / "player.tscn").exists()

    async def test_create_ui_screen_component(self, temp_project):
        tool = CreateComponentTool()
        result = await tool.execute(
            project_root=str(temp_project),
            component_type="ui_screen",
            name="MainMenu",
            behaviors=["input"],
        )
        assert "Created component 'MainMenu'" in result


class TestCreateScriptTool:
    async def test_create_node2d_script(self, temp_project):
        tool = CreateScriptTool()
        path = str(temp_project / "scripts" / "test.gd")
        result = await tool.execute(path=path, template="node2d", class_name="TestNode")
        assert "Created script" in result
        content = (temp_project / "scripts" / "test.gd").read_text()
        assert "class_name TestNode" in content
        assert "extends Node2D" in content

    async def test_create_character_body_script(self, temp_project):
        tool = CreateScriptTool()
        path = str(temp_project / "scripts" / "hero.gd")
        result = await tool.execute(path=path, template="character_body_2d", class_name="Hero")
        content = (temp_project / "scripts" / "hero.gd").read_text()
        assert "extends CharacterBody2D" in content
        assert "_physics_process" in content


class TestSetInputActionTool:
    async def test_set_input_action(self, temp_project):
        # Create a minimal project.godot
        project_file = temp_project / "project.godot"
        project_file.write_text("; Engine Configuration\n")

        tool = SetInputActionTool()
        result = await tool.execute(
            project_root=str(temp_project),
            action_name="move_left",
            keys=["KEY_A", "KEY_LEFT"],
        )
        assert "Set input action 'move_left'" in result
        content = project_file.read_text()
        assert "[input]" in content
        assert "move_left" in content


class TestProjectInspectTool:
    async def test_inspect_empty_project(self, temp_project):
        tool = ProjectInspectTool()
        result = await tool.execute(project_root=str(temp_project))
        assert "Project:" in result
        assert "Scenes: 0" in result
