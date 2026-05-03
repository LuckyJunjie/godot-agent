"""Tests for godot_agent.inspector."""

import pytest
from pathlib import Path

from godot_agent.inspector import ProjectInspector, ProjectReport


class TestProjectInspector:
    def test_empty_project(self, tmp_path):
        inspector = ProjectInspector(str(tmp_path))
        report = inspector.inspect()
        assert report.project_path == str(tmp_path)
        assert "No project.godot found" in report.warnings[0]

    def test_project_with_settings(self, tmp_path):
        project = tmp_path / "project.godot"
        project.write_text("""[application]
config/name="Test Game"
config/features=PackedStringArray("4.2", "Mobile")

[autoload]
GameState="*res://autoload/game_state.tscn"
AudioManager="res://audio/manager.tscn"

[input]
move_left={
"deadzone": 0.5,
"events": []
}
move_right={
"deadzone": 0.5,
"events": []
}
""")
        inspector = ProjectInspector(str(tmp_path))
        report = inspector.inspect()
        assert report.project_name == "Test Game"
        assert report.godot_version == "4.2"
        assert len(report.autoloads) == 2
        assert report.autoloads[0]["name"] == "GameState"
        assert report.autoloads[0]["singleton"] is True
        assert report.autoloads[1]["singleton"] is False
        assert len(report.input_actions) == 2
        assert "move_left" in report.input_actions

    def test_inspect_scenes(self, tmp_path):
        project = tmp_path / "project.godot"
        project.write_text('[application]\nconfig/name="Test"\n')

        scene = tmp_path / "player.tscn"
        scene.write_text("""[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://player.gd" id="1_player"]

[node name="Player" type="CharacterBody2D"]
script = ExtResource("1_player")

[node name="Sprite2D" type="Sprite2D" parent="."]

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
""")
        inspector = ProjectInspector(str(tmp_path))
        report = inspector.inspect()
        assert len(report.scenes) == 1
        assert report.scenes[0].path == "player.tscn"
        assert report.scenes[0].node_count == 3
        assert report.scenes[0].root_name == "Player"
        assert report.scenes[0].root_type == "CharacterBody2D"

    def test_inspect_scripts(self, tmp_path):
        project = tmp_path / "project.godot"
        project.write_text('[application]\nconfig/name="Test"\n')

        script = tmp_path / "player.gd"
        script.write_text("""class_name Player extends CharacterBody2D

signal health_changed(new_health: int)

@export var speed: float = 300.0

func _ready() -> void:
    pass

func _process(delta: float) -> void:
    pass
""")
        inspector = ProjectInspector(str(tmp_path))
        report = inspector.inspect()
        assert len(report.scripts) == 1
        assert report.scripts[0].path == "player.gd"
        assert report.scripts[0].class_name == "Player"
        assert report.scripts[0].extends == "CharacterBody2D"
        assert report.scripts[0].has_ready is True
        assert report.scripts[0].has_process is True
        assert "health_changed" in report.scripts[0].signals

    def test_compute_stats(self, tmp_path):
        project = tmp_path / "project.godot"
        project.write_text('[application]\nconfig/name="Test"\n')

        scene = tmp_path / "main.tscn"
        scene.write_text('[gd_scene format=3]\n\n[node name="Main" type="Node2D"]\n')

        script = tmp_path / "main.gd"
        script.write_text("extends Node2D\n\nfunc _ready():\n    pass\n")

        inspector = ProjectInspector(str(tmp_path))
        report = inspector.inspect()
        assert report.stats["scene_count"] == 1
        assert report.stats["script_count"] == 1
        assert report.stats["total_lines"] == 5
        assert report.stats["nodes_total"] == 1
