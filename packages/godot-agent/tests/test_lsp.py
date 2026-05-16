"""Tests for LSP module."""

import pytest
from godot_agent.lsp import (
    GDScriptLSPClient, Location, Diagnostic, CompletionItem
)


class TestLocation:
    def test_create_location(self):
        loc = Location(uri="file:///test.gd", range={"start": {"line": 1, "character": 0}})
        assert loc.uri == "file:///test.gd"


class TestDiagnostic:
    def test_create_diagnostic(self):
        diag = Diagnostic(message="Error", severity=1, range={})
        assert diag.message == "Error"
        assert diag.severity == 1


class TestCompletionItem:
    def test_create_item(self):
        item = CompletionItem(label="print", kind=1)
        assert item.label == "print"


class TestGDScriptLSPClient:
    def test_create_client(self):
        client = GDScriptLSPClient()
        assert client.host == "localhost"
        assert client.port == 6005
    
    def test_create_client_custom(self):
        client = GDScriptLSPClient(host="127.0.0.1", port=7000)
        assert client.host == "127.0.0.1"
        assert client.port == 7000
    
    def test_client_default_capabilities(self):
        client = GDScriptLSPClient()
        assert client.capabilities == {}
    
    async def test_is_available_false(self):
        client = GDScriptLSPClient()
        assert await client.is_available() is False
