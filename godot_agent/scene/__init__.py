"""
Godot Agent - Scene Model Parser
Parses and edits .tscn (scene) and .tres (resource) files.
"""

from pathlib import Path
from typing import Optional
import re


class SceneNode:
    """Represents a node in a Godot scene."""
    
    def __init__(self, name: str, type: str, instance: Optional[str] = None):
        self.name = name
        self.type = type
        self.instance = instance
        self.properties: dict = {}
        self.children: list[SceneNode] = []
        self.parent: Optional[SceneNode] = None
    
    def add_child(self, node: 'SceneNode'):
        node.parent = self
        self.children.append(node)
    
    def get_path(self) -> str:
        """Get the node path like 'root/child/grandchild'."""
        if self.parent is None:
            return self.name
        return f"{self.parent.get_path()}/{self.name}"


class SceneDocument:
    """In-memory representation of a .tscn file."""
    
    def __init__(self, path: Optional[str] = None):
        self.path = path
        self.root: Optional[SceneNode] = None
        self.ext_resources: list[str] = []
        self.config: dict = {}
    
    def load(self, path: str) -> 'SceneDocument':
        """Load a .tscn file."""
        self.path = path
        content = Path(path).read_text()
        return self._parse(content)
    
    def _parse(self, content: str) -> 'SceneDocument':
        """Parse .tscn content."""
        # Extract ext_resources
        for line in content.split('\n'):
            if line.startswith('[ext_resource'):
                self.ext_resources.append(line.strip())
        
        # Simple node parsing (for now, just find node declarations)
        # In production, use a proper parser
        return self
    
    def save(self, path: Optional[str] = None):
        """Save to .tscn file."""
        path = path or self.path
        if not path:
            raise ValueError("No path specified")
        
        lines = [f"[gd_scene load_steps={len(self.ext_resources)} format=3]\n"]
        
        # Write ext_resources
        for res in self.ext_resources:
            lines.append(f"{res}\n")
        
        # Simple save (expand for full implementation)
        Path(path).write_text('\n'.join(lines))
    
    def get_node(self, path: str) -> Optional[SceneNode]:
        """Get a node by path."""
        if not self.root:
            return None
        parts = path.split('/')
        current = self.root
        for part in parts:
            if part == current.name:
                continue
            found = None
            for child in current.children:
                if child.name == part:
                    found = child
                    break
            if found:
                current = found
            else:
                return None
        return current
    
    def add_node(self, parent_path: str, name: str, type: str, instance: Optional[str] = None) -> SceneNode:
        """Add a new node."""
        parent = self.get_node(parent_path)
        if not parent:
            raise ValueError(f"Parent node not found: {parent_path}")
        
        node = SceneNode(name, type, instance)
        parent.add_child(node)
        return node
    
    def set_property(self, node_path: str, key: str, value):
        """Set a node property."""
        node = self.get_node(node_path)
        if not node:
            raise ValueError(f"Node not found: {node_path}")
        node.properties[key] = value
    
    def connect_signal(self, from_path: str, signal: str, to_path: str, method: str, binds: Optional[list] = None):
        """Connect a signal between nodes."""
        # Placeholder for signal connection logic
        pass


class ResourceDocument:
    """In-memory representation of a .tres file."""
    
    def __init__(self, path: Optional[str] = None):
        self.path = path
        self.resource_type: str = ""
        self.properties: dict = {}
    
    def load(self, path: str) -> 'ResourceDocument':
        """Load a .tres file."""
        self.path = path
        content = Path(path).read_text()
        
        # Parse resource type
        for line in content.split('\n'):
            if line.startswith('[gd_resource'):
                # Extract type
                match = re.search(r'type="(\w+)"', line)
                if match:
                    self.resource_type = match.group(1)
                break
        
        # Parse properties (simplified)
        for line in content.split('\n'):
            if '=' in line and not line.startswith('['):
                key, _, value = line.partition('=')
                self.properties[key.strip()] = value.strip().strip('"')
        
        return self
    
    def save(self, path: Optional[str] = None):
        """Save to .tres file."""
        path = path or self.path
        if not path:
            raise ValueError("No path specified")
        
        lines = [
            f'[gd_resource type="{self.resource_type}" load_steps=2 format=3]',
            "",
        ]
        
        for key, value in self.properties.items():
            lines.append(f'{key} = "{value}"')
        
        Path(path).write_text('\n'.join(lines))