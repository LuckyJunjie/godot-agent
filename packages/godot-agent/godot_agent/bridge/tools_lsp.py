"""LSP-based tools for GDScript-aware editing."""

from __future__ import annotations

from typing import Any

from nanobot.agent.tools.base import Tool

from godot_agent.lsp import GDScriptLSPClient


class GDScriptLintTool(Tool):
    """Run GDScript linting via Godot LSP and return diagnostics."""

    @property
    def name(self) -> str:
        return "gd_script_lint"

    @property
    def description(self) -> str:
        return (
            "Check a GDScript file for syntax errors, type mismatches, "
            "and warnings using the Godot LSP server. "
            "Returns a list of diagnostics with line numbers and messages."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to .gd file"}
            },
            "required": ["path"],
        }

    async def execute(self, path: str) -> str:
        client = GDScriptLSPClient()
        if await client.is_available():
            try:
                await client.initialize()
                # Note: get_diagnostics is a placeholder in current LSP client;
                # real implementation would collect server-pushed notifications.
                return f"⚠️ LSP diagnostics not fully implemented yet for {path}"
            except Exception as exc:
                return f"LSP error: {exc}"

        # Fallback: run godot --check-only
        import subprocess

        try:
            result = subprocess.run(
                ["godot", "--headless", "--check-only", "--script", path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return f"✅ {path}: No syntax errors detected"
            return f"❌ {path}:\n{result.stderr}"
        except FileNotFoundError:
            return "⚠️ Godot not installed; cannot lint"
        except subprocess.TimeoutExpired:
            return "⚠️ Godot check timed out"


class GDScriptGotoDefTool(Tool):
    """Find the definition of a symbol in GDScript."""

    @property
    def name(self) -> str:
        return "gd_script_goto_def"

    @property
    def description(self) -> str:
        return "Find where a class, function, or variable is defined in the codebase."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File containing the symbol",
                },
                "line": {
                    "type": "integer",
                    "description": "Line number (0-indexed)",
                },
                "character": {
                    "type": "integer",
                    "description": "Column number (0-indexed)",
                },
            },
            "required": ["path", "line", "character"],
        }

    async def execute(self, path: str, line: int, character: int) -> str:
        client = GDScriptLSPClient()
        if not await client.is_available():
            return "⚠️ LSP server not available"
        try:
            await client.initialize()
            loc = await client.goto_definition(path, line, character)
            if loc:
                return f"Defined at: {loc.uri}:{loc.range.start.line}"
            return "Definition not found"
        except Exception as exc:
            return f"LSP error: {exc}"
