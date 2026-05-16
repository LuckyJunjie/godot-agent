"""Tests for GDD res:// path handling."""

import pytest
from pathlib import Path

from godot_agent.gdd import GDDEngine


class TestGDDResPath:
    def test_validate_traceability_with_res_paths(self, temp_project):
        engine = GDDEngine(str(temp_project))
        engine.initialize()

        # Create a story with res:// paths
        engine.create_story(
            story_id="001",
            title="Test",
            content="Test story",
        )
        # Manually update with res:// paths
        engine.update_story(
            "001",
            scenes=["res://scenes/main.tscn"],
            scripts=["res://scripts/player.gd"],
            tests=["res://tests/test_player.gd"],
        )

        # Create the actual files
        (temp_project / "scenes").mkdir(parents=True, exist_ok=True)
        (temp_project / "scripts").mkdir(parents=True, exist_ok=True)
        (temp_project / "tests").mkdir(parents=True, exist_ok=True)
        (temp_project / "scenes" / "main.tscn").write_text("[gd_scene]", encoding="utf-8")
        (temp_project / "scripts" / "player.gd").write_text("extends Node2D", encoding="utf-8")
        (temp_project / "tests" / "test_player.gd").write_text("extends Node2D", encoding="utf-8")

        result = engine.validate_traceability()
        assert result["valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_traceability_missing_res_paths(self, temp_project):
        engine = GDDEngine(str(temp_project))
        engine.initialize()

        engine.create_story(
            story_id="001",
            title="Test",
            content="Test story",
        )
        engine.update_story(
            "001",
            scenes=["res://scenes/missing.tscn"],
            scripts=[],
            tests=[],
        )

        result = engine.validate_traceability()
        assert result["valid"] is False
        assert "Missing scene: res://scenes/missing.tscn" in result["issues"]

    def test_resolve_path_plain(self, temp_project):
        engine = GDDEngine(str(temp_project))
        assert engine._resolve_path("scripts/test.gd") == temp_project / "scripts" / "test.gd"

    def test_resolve_path_res(self, temp_project):
        engine = GDDEngine(str(temp_project))
        assert engine._resolve_path("res://scripts/test.gd") == temp_project / "scripts" / "test.gd"
