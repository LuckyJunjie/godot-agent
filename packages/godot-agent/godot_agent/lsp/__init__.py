"""
GDScript LSP Client
Connects to Godot's built-in GDScript language server.
"""

import asyncio
import json
from typing import Optional, Any
from dataclasses import dataclass


@dataclass
class Location:
    """Represents a location in a file."""
    uri: str
    range: dict  # {"start": {"line": int, "character": int}, "end": ...}


@dataclass
class Diagnostic:
    """Represents a code diagnostic."""
    message: str
    severity: int  # 1=error, 2=warning, 3=info
    range: dict


@dataclass
class CompletionItem:
    """Represents a completion suggestion."""
    label: str
    kind: int
    detail: Optional[str] = None


class GDScriptLSPClient:
    """Async LSP client over TCP for GDScript."""
    
    def __init__(self, host: str = "localhost", port: int = 6005):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.capabilities: dict = {}
        self.project_root: Optional[str] = None
    
    async def connect(self) -> bool:
        """Connect to Godot LSP server."""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            return True
        except (ConnectionRefusedError, OSError):
            return False
    
    async def initialize(self, project_root: str | None = None) -> dict:
        """Send LSP initialize request."""
        if project_root:
            self.project_root = project_root
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "processId": None,
                "rootUri": f"file://{project_root}",
                "capabilities": {}
            }
        }
        
        response = await self._send_request(request)
        
        if response and "result" in response:
            self.capabilities = response["result"].get("capabilities", {})
        
        return self.capabilities
    
    async def _send_request(self, request: dict) -> Optional[dict]:
        """Send a JSON-RPC request."""
        if not self.writer:
            return None
        
        try:
            message = json.dumps(request) + "\n"
            self.writer.write(message.encode())
            await self.writer.drain()
            
            # Read response
            if self.reader:
                response_line = await self.reader.readline()
                if response_line:
                    return json.loads(response_line.decode())
        except (json.JSONDecodeError, OSError, asyncio.CancelledError) as exc:
            return {"error": str(exc)}

        return None
    
    async def goto_definition(self, file: str, line: int, column: int) -> Optional[Location]:
        """Find definition at position."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {"uri": f"file://{file}"},
                "position": {"line": line, "character": column}
            }
        }
        
        response = await self._send_request(request)
        
        if response and "result" in response:
            result = response["result"]
            if result:
                return Location(
                    uri=result.get("uri", ""),
                    range=result.get("range", {})
                )
        
        return None
    
    async def get_diagnostics(self, file: str) -> list[Diagnostic]:
        """Get diagnostics for file."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/publishDiagnostics",
            "params": {
                "textDocument": {"uri": f"file://{file}"},
                "diagnostics": []
            }
        }
        
        # This is a placeholder - in practice, diagnostics come via notification
        return []
    
    async def completion(self, file: str, line: int, column: int) -> list[CompletionItem]:
        """Get completions at position."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {"uri": f"file://{file}"},
                "position": {"line": line, "character": column}
            }
        }
        
        response = await self._send_request(request)
        
        if response and "result" in response:
            items = response["result"]
            if isinstance(items, list):
                return [
                    CompletionItem(
                        label=item.get("label", ""),
                        kind=item.get("kind", 1),
                        detail=item.get("detail")
                    )
                    for item in items
                ]
        
        return []
    
    async def hover(self, file: str, line: int, column: int) -> Optional[str]:
        """Get hover info at position."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {"uri": f"file://{file}"},
                "position": {"line": line, "character": column}
            }
        }
        
        response = await self._send_request(request)
        
        if response and "result" in response:
            result = response["result"]
            if result and result.get("contents"):
                return result["contents"].get("value", "")
        
        return None
    
    async def close(self):
        """Close the LSP connection."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def is_available(self) -> bool:
        """Check if LSP server is available, attempting to connect if needed."""
        if self.writer is not None:
            return True
        return await self.connect()