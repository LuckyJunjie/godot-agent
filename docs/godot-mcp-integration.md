# Godot Agent — MCP Integration Guide

## 1. Overview

Godot Agent extends nanobot's MCP support with three Godot-specific servers:

| Server | Repository | Role |
|---|---|---|
| `godot-mcp` | `github.com/satelliteoflove/godot-mcp` | Direct editor control |
| `godotiq` | `github.com/salvo10f/godotiq` | Scene/node intelligence |
| `godogen` | `github.com/htdt/godogen` | Code generation skills |

All three are registered under `tools.mcpServers` and auto-discovered on startup.

---

## 2. godot-mcp (Editor Control)

### 2.1 Capabilities
- **Scene tree introspection**: list nodes, inspect properties, get signal connections
- **Node manipulation**: add/remove nodes, set properties, call methods
- **Editor commands**: play scene, pause, stop, capture screenshot
- **File system**: read/write files within the project
- **Output log**: stream Godot output/errors to the agent

### 2.2 Setup

```json
{
  "tools": {
    "mcpServers": {
      "godot-editor": {
        "command": "godot",
        "args": [
          "--path", "./my_game",
          "--script", "res://addons/godot-mcp/server.gd"
        ],
        "enabledTools": ["*"]
      }
    }
  }
}
```

### 2.3 Key Tools

| Tool | Description |
|---|---|
| `get_scene_tree()` | Returns full scene tree as JSON |
| `get_node_properties(path)` | Returns exported properties of a node |
| `set_node_property(path, property, value)` | Sets a property (type-safe) |
| `call_node_method(path, method, args)` | Calls a method on a node |
| `editor_play_scene(path)` | Plays a scene in the editor |
| `editor_capture_viewport()` | Returns base64 PNG of current viewport |

### 2.4 Security
- `godot-mcp` runs inside the Godot process; it can execute arbitrary GDScript.
- Always enable `tools.godot.sandbox` so the agent cannot touch files outside `projectPath`.
- Use `allowFrom` to restrict which chat channels can trigger editor commands.

---

## 3. godotiq (Scene Intelligence)

### 3.1 Capabilities
- **Semantic search**: "find the player controller script"
- **Dependency graph**: map which scenes depend on which scripts/resources
- **Performance hints**: identify nodes with expensive shaders, large textures
- **Best-practice lint**: detect anti-patterns (cyclic references, missing type hints)

### 3.2 Setup

```json
{
  "tools": {
    "mcpServers": {
      "godotiq": {
        "command": "npx",
        "args": ["-y", "@godotiq/mcp-server", "--project", "./my_game"],
        "toolTimeout": 60
      }
    }
  }
}
```

### 3.3 Key Tools

| Tool | Description |
|---|---|
| `query_project(query)` | Natural-language search across scenes, scripts, resources |
| `get_dependencies(path)` | Returns dependency graph for a scene or script |
| `lint_project(rules)` | Runs lint rules and returns violations |
| `suggest_optimization(target)` | Performance suggestions for a scene or node |

### 3.4 Integration Pattern

```
User: "Why is the main level so slow?"
→ Agent calls godotiq.suggest_optimization("res://scenes/main_level.tscn")
→ godotiq returns: "Node 'Particles' has 10k particles with collision enabled"
→ Agent proposes fix: disable collision or reduce count
→ User approves → Agent edits scene via godot-mcp or scene_edit tool
```

---

## 4. godogen (Skill / Code Generation)

### 4.1 Capabilities
`godogen` is not a traditional MCP server; it is a **skill pack** that the Godot Agent loads and exposes as MCP-compatible tools.

Built-in skills:
- **State Machine Generator**: `generate_state_machine(name, states, transitions)`
- **Component Generator**: `generate_component(type, properties, signals)`
- **UI Screen Generator**: `generate_ui_screen(layout_spec, theme)`
- **Input Map Generator**: `generate_input_map(actions)`
- **Animation Tree Generator**: `generate_animation_tree(spritesheet, states)`

### 4.2 Setup

Godogen skills are bundled with the agent. No external server required.

```json
{
  "godot": {
    "godogenSkillsDir": "~/.godot-agent/skills/godogen"
  }
}
```

### 4.3 Skill Registration Flow

```python
# godot_agent/godogen/integrator.py

class GodogenIntegrator:
    def load_all(self) -> list[ToolSpec]:
        skills = []
        for skill_file in self.skills_dir.glob("*.yaml"):
            spec = GodogenSkillSpec.from_yaml(skill_file)
            skills.append(spec.to_mcp_tool_spec())
        return skills
```

Each skill defines:
- `name`: tool name (e.g., `generate_state_machine`)
- `description`: LLM-visible description
- `inputSchema`: JSON schema for arguments
- `template`: Jinja2 template producing GDScript / scene / resource output
- `postActions`: optional follow-up (e.g., auto-run harness)

### 4.4 Example Skill: State Machine

```yaml
# skills/state_machine.yaml
name: generate_state_machine
description: >
  Generate a GDScript state machine class with enter/exit/update handlers
  and automatic state transition validation.
inputSchema:
  type: object
  properties:
    class_name:
      type: string
    states:
      type: array
      items:
        type: object
        properties:
          name: { type: string }
          enter: { type: string }
          update: { type: string }
          exit: { type: string }
    transitions:
      type: array
      items:
        type: object
        properties:
          from: { type: string }
          to: { type: string }
          condition: { type: string }
template: |
  class_name {{ class_name }} extends Node
  
  enum State {
  {% for s in states %}
    {{ s.name | upper }}{% if not loop.last %},{% endif %}
  {% endfor %}
  }
  
  var current_state: State = State.{{ states[0].name | upper }}
  
  func transition_to(new_state: State) -> void:
    # validation generated from transitions...
```

---

## 5. Unified MCP Tool Registry

On startup, Godot Agent merges:
1. nanobot built-in tools (`web_search`, `shell`, `read_file`, etc.)
2. External MCP servers (`godot-mcp`, `godotiq`, filesystem, etc.)
3. Godogen skills (wrapped as pseudo-MCP tools)
4. Godot-native tools (`scene_edit`, `gdscript_edit`, `asset_generate`, etc.)

The LLM receives a single unified tool list. It does not need to know which backend serves which tool.

### 5.1 Tool Naming Conventions

| Prefix | Source |
|---|---|
| `mcp_` | External MCP server (nanobot convention) |
| `gd_` | Godot-native agent tool |
| `godogen_` | Godogen skill tool |
| (no prefix) | nanobot built-in |

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `godot-mcp` tools timeout | Editor not running | Start Godot with the MCP addon enabled |
| `godotiq` returns empty | Project not indexed | Run `godotiq --index` first |
| Duplicate tool names | MCP + native overlap | Use `enabledTools` filter in config |
| LSP diagnostics stale | Godot LSP not connected | Check `godot.lspPort` matches editor setting |
