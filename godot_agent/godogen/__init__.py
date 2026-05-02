"""
Godogen Integrator
Loads godogen skill packs as MCP-native tools.
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
import json


@dataclass
class ToolSpec:
    """Specification for a tool."""
    name: str
    description: str
    parameters: list[dict] = field(default_factory=list)
    code_template: Optional[str] = None


class GodogenIntegrator:
    """Discovers godogen skills and registers them as agent tools."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.skills_dir = self.project_root / "skills"
        self.tools: list[ToolSpec] = []
    
    def load_skill_pack(self, path: str) -> list[ToolSpec]:
        """Load a skill pack from path."""
        skill_path = Path(path)
        
        if not skill_path.exists():
            return []
        
        tools = []
        
        # Look for skill files (e.g., skill_*.py or skill_*.gd)
        for skill_file in skill_path.glob("skill_*"):
            tool = self._parse_skill(skill_file)
            if tool:
                tools.append(tool)
        
        self.tools.extend(tools)
        return tools
    
    def _parse_skill(self, path: Path) -> Optional[ToolSpec]:
        """Parse a skill file."""
        content = path.read_text()
        
        if path.suffix == ".py":
            # Python skill file
            return self._parse_python_skill(content, path.stem)
        elif path.suffix == ".gd":
            # GDScript skill file
            return self._parse_gdscript_skill(content, path.stem)
        
        return None
    
    def _parse_python_skill(self, content: str, name: str) -> Optional[ToolSpec]:
        """Parse Python skill."""
        # Extract docstring for description
        lines = content.split('\n')
        description = name
        
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                if line.count('"""') == 2 or line.count("'''") == 2:
                    description = line.strip().strip('"""').strip("'''")
                    break
                # Multi-line docstring
                doc_lines = []
                for j in range(i+1, len(lines)):
                    if '"""' in lines[j] or "'''" in lines[j]:
                        description = '\n'.join(doc_lines)
                        break
                    doc_lines.append(lines[j])
                break
        
        return ToolSpec(
            name=f"generate_{name}",
            description=description,
            parameters=self._extract_parameters(content)
        )
    
    def _parse_gdscript_skill(self, content: str, name: str) -> Optional[ToolSpec]:
        """Parse GDScript skill."""
        # Extract comments for description
        description = name
        
        for line in content.split('\n'):
            if line.strip().startswith('##') or line.strip().startswith('#'):
                desc = line.strip().lstrip('#').strip()
                if desc:
                    description = desc
                    break
        
        return ToolSpec(
            name=f"gd_generate_{name}",
            description=description,
            parameters=[]
        )
    
    def _extract_parameters(self, content: str) -> list[dict]:
        """Extract function parameters."""
        params = []
        
        # Simple regex for def/fn statements
        import re
        pattern = r'def\s+\w+\(([^)]*)\)'
        
        for match in re.finditer(pattern, content):
            args = match.group(1)
            if args:
                for arg in args.split(','):
                    arg = arg.strip()
                    if arg and '=' in arg:
                        name, default = arg.split('=', 1)
                        params.append({
                            "name": name.strip(),
                            "default": default.strip()
                        })
                    elif arg:
                        params.append({"name": arg, "default": None})
        
        return params
    
    def register_as_mcp_tools(self) -> list[dict]:
        """Register tools as MCP-compatible format."""
        mcp_tools = []
        
        for tool in self.tools:
            mcp_tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        p["name"]: {"type": "string"}
                        for p in tool.parameters
                    }
                }
            })
        
        return mcp_tools
    
    def generate_state_machine(self, name: str, states: list[str], transitions: dict) -> str:
        """Generate a state machine GDScript."""
        lines = [
            "extends Node",
            "",
            f"class_name {name}",
            "",
            "# States",
        ]
        
        for state in states:
            lines.append(f"enum State {{ {state} }}")
        
        lines.extend([
            "",
            "var current_state: State",
            "",
            "func _ready():",
            "    current_state = State." + states[0],
            "",
            "func _process(delta):",
            "    match current_state:",
        ])
        
        for state, target in transitions.items():
            lines.append(f"        State.{state}:")
            lines.append(f"            # Handle {state} -> {target}")
        
        return '\n'.join(lines)
    
    def generate_component(self, type: str, properties: dict) -> str:
        """Generate a Godot component."""
        lines = [
            "extends Node",
            "",
            f"class_name {type.capitalize()}Component",
            "",
            "# Properties",
        ]
        
        for prop, prop_type in properties.items():
            if prop_type == "int":
                lines.append(f"var {prop}: int = 0")
            elif prop_type == "float":
                lines.append(f"var {prop}: float = 0.0")
            elif prop_type == "string":
                lines.append(f"var {prop}: String = \"\"")
            elif prop_type == "bool":
                lines.append(f"var {prop}: bool = false")
            else:
                lines.append(f"var {prop}")
        
        lines.extend([
            "",
            "func _ready():",
            "    pass",
            "",
            "func _process(delta):",
            "    pass",
        ])
        
        return '\n'.join(lines)
    
    def generate_ui_screen(self, layout: dict) -> str:
        """Generate a UI screen."""
        lines = [
            "extends Control",
            "",
            f"class_name {layout.get('name', 'Screen')}Screen",
            "",
        ]
        
        for element in layout.get("elements", []):
            element_type = element.get("type", "Label")
            element_name = element.get("name", "element")
            
            lines.extend([
                f"@onready var {element_name}: {element_type} = ${element_name}",
                "",
                f"func _ready():",
                f"    ${element_name}.text = \"{element.get('text', '')}\"",
            ])
        
        return '\n'.join(lines)