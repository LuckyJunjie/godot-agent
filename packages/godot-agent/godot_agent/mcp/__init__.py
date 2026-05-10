"""
MCP Integration for Godot Agent.
Supports godot-mcp, godotiq, and godogen MCP servers.
"""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    transport: str = "stdio"  # stdio, http, sse
    url: Optional[str] = None


@dataclass
class MCPTool:
    """An MCP tool specification."""
    name: str
    description: str
    input_schema: dict[str, Any]
    server: str


class MCPClient:
    """MCP client for connecting to Godot MCP servers."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.servers: dict[str, MCPServerConfig] = {}
        self.tools: list[MCPTool] = []
        self.processes: dict[str, subprocess.Popen] = {}
    
    def add_server(self, name: str, config: MCPServerConfig):
        """Add an MCP server configuration."""
        self.servers[name] = config
    
    def add_godot_mcp(self):
        """Add godot-mcp server."""
        self.add_server("godot-mcp", MCPServerConfig(
            name="godot-mcp",
            command="godot",
            args=["--script", "addons/godot-mcp/server.gd"],
            transport="stdio"
        ))
    
    def add_godotiq(self):
        """Add godotiq server."""
        self.add_server("godotiq", MCPServerConfig(
            name="godotiq",
            command="npx",
            args=["-y", "@godotiq/mcp-server"],
            transport="stdio"
        ))
    
    def add_godogen(self):
        """Add godogen as MCP tools."""
        self.add_server("godogen", MCPServerConfig(
            name="godogen",
            command="python3",
            args=["-m", "godot_agent.godogen"],
            transport="stdio"
        ))
    
    async def start_server(self, name: str) -> bool:
        """Start an MCP server."""
        if name not in self.servers:
            return False
        
        config = self.servers[name]
        
        try:
            proc = await asyncio.create_subprocess_exec(
                config.command,
                *config.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root),
                env={**subprocess.os.environ, **config.env}
            )
            self.processes[name] = proc
            return True
        except FileNotFoundError:
            return False
    
    async def stop_server(self, name: str):
        """Stop an MCP server."""
        if name in self.processes:
            proc = self.processes[name]
            proc.terminate()
            await proc.wait()
            del self.processes[name]
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: dict) -> Optional[dict]:
        """Call an MCP tool."""
        if server_name not in self.processes:
            return None
        
        proc = self.processes[server_name]
        
        # Send JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": f"tools/{tool_name}",
            "params": arguments
        }
        
        try:
            proc.stdin.write(json.dumps(request).encode() + b"\n")
            await proc.stdin.drain()
            
            # Read response
            response_line = await asyncio.wait_for(
                proc.stdout.readline(),
                timeout=30.0
            )
            
            if response_line:
                return json.loads(response_line.decode())
        except (asyncio.TimeoutError, json.JSONDecodeError, KeyError):
            pass
        
        return None
    
    async def list_tools(self, server_name: str) -> list[MCPTool]:
        """List available tools from a server."""
        if server_name not in self.processes:
            return []
        
        proc = self.processes[server_name]
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        try:
            proc.stdin.write(json.dumps(request).encode() + b"\n")
            await proc.stdin.drain()
            
            response_line = await asyncio.wait_for(
                proc.stdout.readline(),
                timeout=10.0
            )
            
            if response_line:
                data = json.loads(response_line.decode())
                tools = data.get("result", [])
                return [
                    MCPTool(
                        name=t["name"],
                        description=t.get("description", ""),
                        input_schema=t.get("inputSchema", {}),
                        server=server_name
                    )
                    for t in tools
                ]
        except (asyncio.TimeoutError, json.JSONDecodeError):
            pass
        
        return []
    
    async def start_all(self) -> dict[str, bool]:
        """Start all configured servers."""
        results = {}
        for name in self.servers:
            results[name] = await self.start_server(name)
        return results
    
    async def stop_all(self):
        """Stop all servers."""
        for name in list(self.processes.keys()):
            await self.stop_server(name)
    
    def get_tools_by_server(self, server_name: str) -> list[MCPTool]:
        """Get tools for a specific server."""
        return [t for t in self.tools if t.server == server_name]
    
    def register_tool(self, tool: MCPTool):
        """Register a tool."""
        self.tools.append(tool)


# Factory functions
def create_godot_mcp_client(project_root: str) -> MCPClient:
    """Create a client with all Godot MCP servers."""
    client = MCPClient(project_root)
    client.add_godot_mcp()
    client.add_godotiq()
    client.add_godogen()
    return client
