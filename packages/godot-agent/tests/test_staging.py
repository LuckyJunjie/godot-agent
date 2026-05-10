"""Tests for StagingArea atomic operations."""

import pytest
from pathlib import Path

from godot_agent.staging import StagingArea, StagedChange


class TestStagingArea:
    def test_write_file_and_preview(self, temp_project):
        staging = StagingArea(str(temp_project))
        staging.write_file("scripts/test.gd", "extends Node\n")
        preview = staging.preview()
        assert "WRITE scripts/test.gd" in preview
        # Should not exist in project yet
        assert not (temp_project / "scripts" / "test.gd").exists()

    def test_apply_and_cleanup(self, temp_project):
        staging = StagingArea(str(temp_project))
        staging.write_file("scripts/player.gd", "extends CharacterBody2D\n")
        staging.apply()
        assert (temp_project / "scripts" / "player.gd").exists()
        content = (temp_project / "scripts" / "player.gd").read_text()
        assert "CharacterBody2D" in content
        staging.cleanup()

    def test_rollback_restores_original(self, temp_project):
        # Create original file
        original = temp_project / "scripts" / "original.gd"
        original.parent.mkdir(parents=True, exist_ok=True)
        original.write_text("original content")

        staging = StagingArea(str(temp_project))
        staging.write_file("scripts/original.gd", "modified content")
        staging.apply()
        assert original.read_text() == "modified content"

        staging.rollback()
        assert original.read_text() == "original content"
        staging.cleanup()

    def test_delete_file_staging(self, temp_project):
        # Create a file to delete
        target = temp_project / "scenes" / "old.tscn"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("[gd_scene]\n")

        staging = StagingArea(str(temp_project))
        staging.delete_file("scenes/old.tscn")
        staging.apply()
        assert not target.exists()
        staging.cleanup()
