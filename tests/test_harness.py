"""Tests for harness module."""

import pytest
from godot_agent.harness import HarnessRunner, TestResult, SceneResult


class TestTestResult:
    def test_create_passed_result(self):
        result = TestResult(passed=True, message="All passed", duration=1.5)
        assert result.passed is True
        assert result.duration == 1.5

    def test_create_failed_result(self):
        result = TestResult(passed=False, message="Failed", duration=0.5, details={"error": "test"})
        assert result.passed is False
        assert result.details["error"] == "test"


class TestSceneResult:
    def test_create_loaded_result(self):
        result = SceneResult(loaded=True, scene_path="player.tscn", duration=2.0)
        assert result.loaded is True
        assert result.scene_path == "player.tscn"

    def test_create_failed_result(self):
        result = SceneResult(loaded=False, scene_path="missing.tscn", duration=0.0, error="Not found")
        assert result.loaded is False
        assert result.error == "Not found"


class TestHarnessRunner:
    def test_create_runner(self, temp_project):
        runner = HarnessRunner(str(temp_project))
        assert runner.project_root == temp_project
        assert runner.godot_path == "godot"

    def test_create_runner_custom_godot(self, temp_project):
        runner = HarnessRunner(str(temp_project), godot_path="/usr/bin/godot")
        assert runner.godot_path == "/usr/bin/godot"

    def test_run_unit_godot_not_found(self, temp_project):
        runner = HarnessRunner(str(temp_project), godot_path="nonexistent_godot")
        import asyncio
        result = asyncio.run(runner.run_unit("test.gd"))
        assert result.passed is False
        assert "not found" in result.message.lower()

    def test_run_scene_godot_not_found(self, temp_project):
        runner = HarnessRunner(str(temp_project), godot_path="nonexistent_godot")
        import asyncio
        result = asyncio.run(runner.run_scene("player.tscn"))
        assert result.loaded is False

    def test_check_syntax_errors_godot_not_found(self, temp_project):
        runner = HarnessRunner(str(temp_project), godot_path="nonexistent_godot")
        errors = runner.check_syntax_errors("test.gd")
        assert len(errors) > 0

    def test_run_gut_suite_missing(self, temp_project):
        runner = HarnessRunner(str(temp_project))
        import asyncio
        result = asyncio.run(runner.run_gut_suite("test.gd"))
        assert result.passed is False
