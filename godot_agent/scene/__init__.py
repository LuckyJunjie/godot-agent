"""
Godot Agent - Scene Model Parser
Parses and edits .tscn (scene) and .tres (resource) files.
"""

from pathlib import Path
from typing import Optional
import re


class SceneNode:
    """Represents a node in a Godot scene."""
    
    def __init__(self, name: str, type: str = "", instance: Optional[str] = None, parent: Optional[str] = None):
        self.name = name
        self.type = type
        self.instance = instance
        self.parent_path = parent
        self.properties: dict[str, str] = {}
        self.children: list['SceneNode'] = []
        self.parent_node: Optional['SceneNode'] = None
    
    @property
    def parent(self) -> Optional['SceneNode']:
        """Backwards-compatible alias for parent_node."""
        return self.parent_node
    
    def add_child(self, node: 'SceneNode'):
        node.parent_node = self
        self.children.append(node)
    
    def get_path(self) -> str:
        """Get the node path like 'root/child/grandchild'."""
        if self.parent_node is None:
            return self.name
        return f"{self.parent_node.get_path()}/{self.name}"
    
    def to_tscn(self, depth: int = 0) -> str:
        """Serialize this node to .tscn format."""
        indent = "\t" * depth
        lines = []
        
        # Node header
        header = f"[node name=\"{self.name}\""
        if self.type:
            header += f' type="{self.type}"'
        if self.instance:
            header += f' instance=ExtResource("{self.instance}")'
        if self.parent_path and self.parent_path != ".":
            header += f' parent="{self.parent_path}"'
        header += "]"
        lines.append(indent + header)
        
        # Properties
        for key, value in self.properties.items():
            lines.append(f"{indent}{key} = {value}")
        
        # Children
        for child in self.children:
            lines.append("")
            lines.extend(child.to_tscn(depth).split("\n"))
        
        return "\n".join(lines)


class SceneDocument:
    """In-memory representation of a .tscn file."""
    
    def __init__(self, path: Optional[str] = None):
        self.path = path
        self.root: Optional[SceneNode] = None
        self.ext_resources: list[dict] = []
        self.sub_resources: list[dict] = []
        self.connections: list[dict] = []
        self._node_map: dict[str, SceneNode] = {}
    
    def load(self, path: str) -> 'SceneDocument':
        """Load a .tscn file."""
        self.path = path
        content = Path(path).read_text()
        return self._parse(content)
    
    def _parse(self, content: str) -> 'SceneDocument':
        """Parse .tscn content."""
        lines = content.split('\n')
        i = 0
        current_node: Optional[SceneNode] = None
        current_section: Optional[str] = None
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith(";"):
                i += 1
                continue
            
            # Section headers
            if stripped.startswith('['):
                current_node = None
                current_section = None
                
                if stripped.startswith('[gd_scene'):
                    pass  # Root scene header
                elif stripped.startswith('[ext_resource'):
                    res = self._parse_header(stripped)
                    self.ext_resources.append(res)
                elif stripped.startswith('[sub_resource'):
                    res = self._parse_header(stripped)
                    self.sub_resources.append(res)
                elif stripped.startswith('[node'):
                    node_info = self._parse_header(stripped)
                    name = node_info.get("name", "")
                    node_type = node_info.get("type", "")
                    instance = node_info.get("instance", "")
                    parent = node_info.get("parent", ".")
                    
                    # Extract instance ExtResource id if present
                    if instance.startswith('ExtResource('):
                        instance = re.search(r'ExtResource\("([^"]+)"\)', instance)
                        if instance:
                            instance = instance.group(1)
                    
                    node = SceneNode(name=name, type=node_type, instance=instance or None, parent=parent)
                    current_node = node
                    self._node_map[name] = node
                    
                    # Build tree
                    if parent == "." or not parent:
                        self.root = node
                    else:
                        parent_node = self._node_map.get(parent)
                        if parent_node:
                            parent_node.add_child(node)
                        else:
                            # Parent might be a path like "MainMenu/Panel"
                            parent_node = self.get_node(parent)
                            if parent_node:
                                parent_node.add_child(node)
                elif stripped.startswith('[connection'):
                    conn = self._parse_header(stripped)
                    self.connections.append(conn)
            
            elif current_node and '=' in stripped:
                # Property line belonging to current node
                key, _, value = stripped.partition('=')
                current_node.properties[key.strip()] = value.strip()
            
            i += 1
        
        return self
    
    def _parse_header(self, line: str) -> dict[str, str]:
        """Parse a bracketed header like [node name="X" type="Y"]."""
        result: dict[str, str] = {}
        # Match key="value" or key=value patterns
        for match in re.finditer(r'(\w+)\s*=\s*("[^"]*"|[^\s\]]+)', line):
            key = match.group(1)
            value = match.group(2).strip('"')
            result[key] = value
        return result
    
    def save(self, path: Optional[str] = None):
        """Save to .tscn file."""
        path = path or self.path
        if not path:
            raise ValueError("No path specified")
        
        lines: list[str] = []
        
        # Scene header
        load_steps = len(self.ext_resources) + len(self.sub_resources)
        lines.append(f"[gd_scene load_steps={load_steps} format=3 uid://{self._generate_uid()}]")
        lines.append("")
        
        # External resources
        for res in self.ext_resources:
            if isinstance(res, str):
                lines.append(res)
            else:
                res_line = "[ext_resource"
                for k, v in res.items():
                    res_line += f' {k}="{v}"'
                res_line += "]"
                lines.append(res_line)
        if self.ext_resources:
            lines.append("")
        
        # Sub resources
        for res in self.sub_resources:
            if isinstance(res, str):
                lines.append(res)
            else:
                res_line = "[sub_resource"
                for k, v in res.items():
                    if k == "type":
                        res_line += f' {k}="{v}"'
                    else:
                        res_line += f' {k}="{v}"'
                res_line += "]"
                lines.append(res_line)
        if self.sub_resources:
            lines.append("")
        
        # Node tree
        if self.root:
            lines.append(self.root.to_tscn())
            lines.append("")
        
        # Connections
        for conn in self.connections:
            conn_line = f"[connection signal=\"{conn.get('signal', '')}\" from=\"{conn.get('from', '')}\" to=\"{conn.get('to', '')}\" method=\"{conn.get('method', '')}\""
            if conn.get("flags"):
                conn_line += f' flags={conn["flags"]}'
            conn_line += "]"
            lines.append(conn_line)
        
        Path(path).write_text('\n'.join(lines))
    
    def _generate_uid(self) -> str:
        """Generate a fake Godot UID."""
        import hashlib
        seed = str(self.path or "scene")
        return hashlib.sha256(seed.encode()).hexdigest()[:13]
    
    def get_node(self, path: str) -> Optional[SceneNode]:
        """Get a node by path."""
        if not self.root:
            return None
        if path == "." or path == self.root.name:
            return self.root
        
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
        self._node_map[name] = node
        return node
    
    def remove_node(self, path: str) -> bool:
        """Remove a node by path."""
        node = self.get_node(path)
        if not node or node.parent_node is None:
            return False
        node.parent_node.children.remove(node)
        del self._node_map[node.name]
        return True
    
    def set_property(self, node_path: str, key: str, value: str):
        """Set a node property."""
        node = self.get_node(node_path)
        if not node:
            raise ValueError(f"Node not found: {node_path}")
        node.properties[key] = value
    
    def connect_signal(self, from_path: str, signal: str, to_path: str, method: str, binds: Optional[list] = None):
        """Connect a signal between nodes."""
        self.connections.append({
            "signal": signal,
            "from": from_path,
            "to": to_path,
            "method": method,
            "flags": "",
        })


class ResourceDocument:
    """In-memory representation of a .tres file."""
    
    def __init__(self, path: Optional[str] = None):
        self.path = path
        self.resource_type: str = ""
        self.properties: dict[str, str] = {}
    
    def load(self, path: str) -> 'ResourceDocument':
        """Load a .tres file."""
        self.path = path
        content = Path(path).read_text()
        
        # Parse resource type
        for line in content.split('\n'):
            if line.startswith('[gd_resource'):
                match = re.search(r'type="(\w+)"', line)
                if match:
                    self.resource_type = match.group(1)
                break
        
        # Parse properties
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
            lines.append(f'{key} = {value}')
        
        Path(path).write_text('\n'.join(lines))
