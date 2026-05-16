"""Tests for LSP bridge tools."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from godot_agent.bridge.tools_lsp import GDScriptLintTool, GDScriptGotoDefTool


class TestGDScriptLintTool:
    async def test_lint_fallback_godot_not_installed(self, temp_project):
        tool = GDScriptLintTool()
        script = temp_project / "test.gd"
        script.write_text("extends Node2D\n", encoding="utf-8")

        result = await tool.execute(path=str(script))
        assert "Godot not installed" in result or "LSP" in result

    async def test_lint_no_syntax_errors(self, temp_project, monkeypatch):
        """Test fallback path when godot returns clean."""
        tool = GDScriptLintTool()
        script = temp_project / "test.gd"
        script.write_text("extends Node2D\n", encoding="utf-8")

        def fake_run(*args, **kwargs):
            class Result:
                returncode = 0
                stderr = ""
            return Result()

        monkeypatch.setattr("subprocess.run", fake_run)
        result = await tool.execute(path=str(script))
        assert "No syntax errors" in result

    async def test_lint_with_errors(self, temp_project, monkeypatch):
        tool = GDScriptLintTool()
        script = temp_project / "test.gd"
        script.write_text("extends Node2D\n", encoding="utf-8")

        def fake_run(*args, **kwargs):
            class Result:
                returncode = 1
                stderr = "Parse error at line 3"
            return Result()

        monkeypatch.setattr("subprocess.run", fake_run)
        result = await tool.execute(path=str(script))
        assert "Parse error" in result

    async def test_lsp_path(self, temp_project, monkeypatch):
        tool = GDScriptLintTool()
        script = temp_project / "test.gd"
        script.write_text("extends Node2D\n", encoding="utf-8")

        mock_client = AsyncMock()
        mock_client.is_available = AsyncMock(return_value=True)
        mock_client.initialize = AsyncMock()
        mock_client.close = AsyncMock()

        monkeypatch.setattr(
            "godot_agent.bridge.tools_lsp.GDScriptLSPClient",
            lambda: mock_client,
        )

        result = await tool.execute(path=str(script))
        assert "not fully implemented" in result
        mock_client.initialize.assert_awaited_once()
        mock_client.close.assert_awaited_once()


class TestGDScriptGotoDefTool:
    async def test_goto_def_not_available(self, temp_project, monkeypatch):
        tool = GDScriptGotoDefTool()

        mock_client = AsyncMock()
        mock_client.is_available = AsyncMock(return_value=False)

        monkeypatch.setattr(
            "godot_agent.bridge.tools_lsp.GDScriptLSPClient",
            lambda: mock_client,
        )

        result = await tool.execute(path=str(temp_project / "test.gd"), line=0, character=0)
        assert "not available" in result

    async def test_goto_def_found(self, temp_project, monkeypatch):
        tool = GDScriptGotoDefTool()

        mock_client = AsyncMock()
        mock_client.is_available = AsyncMock(return_value=True)
        mock_client.initialize = AsyncMock()

        loc = MagicMock()
        loc.uri = "file:///test.gd"
        loc.range.start.line = 5
        mock_client.goto_definition = AsyncMock(return_value=loc)
        mock_client.close = AsyncMock()

        monkeypatch.setattr(
            "godot_agent.bridge.tools_lsp.GDScriptLSPClient",
            lambda: mock_client,
        )

        result = await tool.execute(path=str(temp_project / "test.gd"), line=2, character=5)
        assert "Defined at" in result
        assert "test.gd:5" in result

    async def test_goto_def_not_found(self, temp_project, monkeypatch):
        tool = GDScriptGotoDefTool()

        mock_client = AsyncMock()
        mock_client.is_available = AsyncMock(return_value=True)
        mock_client.initialize = AsyncMock()
        mock_client.goto_definition = AsyncMock(return_value=None)
        mock_client.close = AsyncMock()

        monkeypatch.setattr(
            "godot_agent.bridge.tools_lsp.GDScriptLSPClient",
            lambda: mock_client,
        )

        result = await tool.execute(path=str(temp_project / "test.gd"), line=2, character=5)
        assert "Definition not found" in result
