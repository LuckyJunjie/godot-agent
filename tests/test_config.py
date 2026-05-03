"""Tests for godot_agent.config module."""

import json
import os
from pathlib import Path

import pytest

from godot_agent.config import GodotConfig, AssetsConfig, HarnessConfig, GodotAgentConfig, load_config, save_config


class TestGodotConfig:
    def test_defaults(self):
        cfg = GodotConfig()
        assert cfg.editor_path == "godot"
        assert cfg.project_path == "."
        assert cfg.lsp_port == 6005
        assert cfg.lsp_host == "localhost"
        assert cfg.lsp_auto_connect is True
        assert cfg.headless_args == ["--headless", "--quit"]

    def test_alias_parsing(self):
        raw = {"editorPath": "/usr/bin/godot", "lspPort": 7000}
        cfg = GodotConfig.model_validate(raw)
        assert cfg.editor_path == "/usr/bin/godot"
        assert cfg.lsp_port == 7000


class TestAssetsConfig:
    def test_defaults(self):
        cfg = AssetsConfig()
        assert cfg.image_provider == "dall-e-3"
        assert cfg.audio_provider == "elevenlabs"
        assert cfg.output_dir == "assets/generated"

    def test_api_key_from_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("IMAGE_API_KEY", "sk-test123")
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"assets": {"imageApiKey": "${IMAGE_API_KEY}"}}))
        cfg = load_config(config_file)
        assert cfg.assets.image_api_key == "sk-test123"


class TestHarnessConfig:
    def test_defaults(self):
        cfg = HarnessConfig()
        assert cfg.auto_run is True
        assert cfg.timeout_sec == 30


class TestGodotAgentConfig:
    def test_nested_defaults(self):
        cfg = GodotAgentConfig()
        assert cfg.godot.lsp_port == 6005
        assert cfg.assets.image_provider == "dall-e-3"
        assert cfg.harness.test_dir == "res://tests"


class TestLoadConfig:
    def test_load_from_file(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "godot": {"editorPath": "/opt/godot", "projectPath": "./game"},
            "assets": {"imageProvider": "stable-diffusion"}
        }))
        cfg = load_config(config_file)
        assert cfg.godot.editor_path == "/opt/godot"
        assert cfg.assets.image_provider == "stable-diffusion"

    def test_load_missing_returns_defaults(self, tmp_path):
        cfg = load_config(tmp_path / "nonexistent.json")
        assert cfg.godot.editor_path == "godot"

    def test_env_var_resolution(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GODOT_PATH", "/custom/godot")
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "godot": {"editorPath": "${GODOT_PATH}"}
        }))
        cfg = load_config(config_file)
        assert cfg.godot.editor_path == "/custom/godot"


class TestSaveConfig:
    def test_save_and_reload(self, tmp_path):
        config_file = tmp_path / "saved.json"
        cfg = GodotAgentConfig(
            godot=GodotConfig(editor_path="/usr/godot", project_path="./my_game")
        )
        saved = save_config(cfg, config_file)
        assert saved.exists()
        
        reloaded = load_config(saved)
        assert reloaded.godot.editor_path == "/usr/godot"
        assert reloaded.godot.project_path == "./my_game"
