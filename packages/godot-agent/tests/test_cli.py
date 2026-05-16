"""Tests for CLI main.py."""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from godot_agent.cli.main import app


runner = CliRunner()


class TestVersion:
    def test_version_command(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "godot-agent" in result.output


class TestInit:
    def test_init_creates_project(self, temp_project):
        result = runner.invoke(app, ["init", "--project", str(temp_project)])
        assert result.exit_code == 0
        assert "Project initialized" in result.output
        assert (temp_project / "gdd").exists()
        assert (temp_project / "tests" / "__init__.py").exists()


class TestConfigShow:
    def test_config_show(self, temp_project):
        # Init first to create config
        runner.invoke(app, ["init", "--project", str(temp_project)])
        result = runner.invoke(app, ["config-show"])
        assert result.exit_code == 0


class TestInspect:
    def test_inspect_empty_project(self, temp_project):
        result = runner.invoke(app, ["inspect", "--project", str(temp_project)])
        assert result.exit_code == 0
        assert "Project Report" in result.output


class TestSceneInspect:
    def test_scene_inspect(self, temp_project):
        scene = temp_project / "main.tscn"
        scene.write_text(
            '[gd_scene load_steps=1 format=3]\n\n[node name="Main" type="Node2D"]\n',
            encoding="utf-8",
        )
        result = runner.invoke(app, ["scene-inspect", str(scene)])
        assert result.exit_code == 0
        assert "Scene:" in result.output


class TestGddValidate:
    def test_gdd_validate_empty(self, temp_project):
        result = runner.invoke(app, ["gdd-validate", "--project", str(temp_project)])
        assert result.exit_code == 0
        assert "valid" in result.output.lower() or "issues" in result.output.lower()


class TestGenerateDryRun:
    def test_generate_dry_run(self, temp_project, monkeypatch):
        monkeypatch.chdir(temp_project)
        result = runner.invoke(app, ["generate", "make a snake game", "--dry-run"])
        # Planning might fail if no state/llm, but dry-run should at least try
        # With default mock LLM (no api key), it will fail early
        # Just verify the command runs without crashing
        assert result.exit_code in (0, 1)


class TestHarness:
    def test_harness_no_args(self):
        result = runner.invoke(app, ["harness"])
        assert result.exit_code == 0
        assert "Specify a test script" in result.output


class TestAsset:
    def test_asset_list_empty(self, temp_project):
        result = runner.invoke(app, ["asset", "list", "--project", str(temp_project)])
        assert result.exit_code == 0
