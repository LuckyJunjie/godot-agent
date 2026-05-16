"""
Godogen Integrator
Loads godogen skill packs as MCP-native tools.
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
import json

import yaml


@dataclass
class ToolSpec:
    """Specification for a tool."""
    name: str
    description: str
    parameters: list[dict] = field(default_factory=list)
    code_template: Optional[str] = None
    input_schema: dict = field(default_factory=dict)


class GodogenIntegrator:
    """Discovers godogen skills and registers them as agent tools."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.skills_dir = self.project_root / "skills"
        self.tools: list[ToolSpec] = []
    
    def load_all(self) -> list[ToolSpec]:
        """Load all YAML skills from skills/godogen/."""
        godogen_dir = self.skills_dir / "godogen"
        if not godogen_dir.exists():
            return []

        tools = []
        for skill_file in godogen_dir.glob("*.yaml"):
            tool = self._parse_yaml_skill(skill_file)
            if tool and tool.name not in {t.name for t in self.tools}:
                tools.append(tool)

        self.tools.extend(tools)
        return tools
    
    def load_skill_pack(self, path: str) -> list[ToolSpec]:
        """Load a skill pack from path."""
        skill_path = Path(path)

        if not skill_path.exists():
            return []

        tools = []
        existing_names = {t.name for t in self.tools}

        for skill_file in skill_path.glob("*.yaml"):
            tool = self._parse_yaml_skill(skill_file)
            if tool and tool.name not in existing_names:
                tools.append(tool)

        self.tools.extend(tools)
        return tools
    
    def _parse_yaml_skill(self, path: Path) -> Optional[ToolSpec]:
        """Parse a YAML skill file."""
        try:
            data = yaml.safe_load(path.read_text())
        except Exception:
            return None
        
        if not data or not isinstance(data, dict):
            return None
        
        name = data.get("name", path.stem)
        description = data.get("description", name)
        template = data.get("template", "")
        schema = data.get("inputSchema", {})
        
        # Extract parameter list from schema properties
        params = []
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key, prop in properties.items():
            params.append({
                "name": key,
                "type": prop.get("type", "string"),
                "required": key in required,
                "description": prop.get("description", ""),
            })
        
        return ToolSpec(
            name=name,
            description=description,
            parameters=params,
            code_template=template,
            input_schema=schema,
        )
    
    def _parse_skill(self, path: Path) -> Optional[ToolSpec]:
        """Parse a skill file (legacy: .py / .gd)."""
        content = path.read_text()
        
        if path.suffix == ".py":
            return self._parse_python_skill(content, path.stem)
        elif path.suffix == ".gd":
            return self._parse_gdscript_skill(content, path.stem)
        elif path.suffix == ".yaml":
            return self._parse_yaml_skill(path)
        
        return None
    
    def _parse_python_skill(self, content: str, name: str) -> Optional[ToolSpec]:
        """Parse Python skill."""
        lines = content.split('\n')
        description = name
        
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                if line.count('"""') == 2 or line.count("'''") == 2:
                    description = line.strip().strip('"""').strip("'''")
                    break
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

        import re
        # Regex that handles one level of nested parentheses in type hints
        pattern = r'def\s+\w+\((.*?)\)(?:\s*->|\s*:|\n)'

        for match in re.finditer(pattern, content, re.DOTALL):
            args = match.group(1)
            if args:
                # Split by comma, but respect one level of nesting
                depth = 0
                current = ""
                for char in args:
                    if char in "([":
                        depth += 1
                    elif char in "])":
                        depth -= 1
                    elif char == "," and depth == 0:
                        arg = current.strip()
                        if arg and "=" in arg:
                            name, default = arg.split("=", 1)
                            params.append({
                                "name": name.strip(),
                                "default": default.strip()
                            })
                        elif arg:
                            params.append({"name": arg, "default": None})
                        current = ""
                        continue
                    current += char
                # Handle last arg
                arg = current.strip()
                if arg and "=" in arg:
                    name, default = arg.split("=", 1)
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
                "inputSchema": tool.input_schema or {
                    "type": "object",
                    "properties": {
                        p["name"]: {"type": "string"}
                        for p in tool.parameters
                    }
                }
            })
        
        return mcp_tools
    
    def render_skill(self, tool_name: str, context: dict) -> str:
        """Render a skill template with Jinja2 context."""
        try:
            from jinja2 import Template
        except ImportError:
            # Fallback: simple string interpolation
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if not tool or not tool.code_template:
                return ""
            result = tool.code_template
            for key, value in context.items():
                result = result.replace(f"{{{{ {key} }}}}", str(value))
            return result
        
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool or not tool.code_template:
            return ""
        
        template = Template(tool.code_template, trim_blocks=True, lstrip_blocks=True)
        return template.render(**context)
    
    def generate_state_machine(self, name: str, states: list[str], transitions: dict) -> str:
        """Generate a state machine GDScript."""
        if not states:
            return f"extends Node\n\nclass_name {name}\n\n# No states defined\n"

        tool = next((t for t in self.tools if t.name == "generate_state_machine"), None)
        if tool:
            return self.render_skill("generate_state_machine", {
                "class_name": name,
                "states": [{"name": s} for s in states],
                "transitions": transitions,
            })

        # Fallback inline template
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
            f"    current_state = State.{states[0]}",
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
        tool = next((t for t in self.tools if t.name == "generate_component"), None)
        if tool:
            return self.render_skill("generate_component", {
                "class_name": f"{type.capitalize()}Component",
                "extends": "Node",
                "properties": [
                    {"name": k, "type": v, "default": "0" if v == "int" else "0.0" if v == "float" else "\"\"" if v == "String" else "false" if v == "bool" else "null", "export": True}
                    for k, v in properties.items()
                ],
            })
        
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
        tool = next((t for t in self.tools if t.name == "generate_ui_screen"), None)
        if tool:
            return self.render_skill("generate_ui_screen", layout)
        
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
    
