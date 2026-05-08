# Godogen Skills

Built-in skill templates for the Godot Agent.

## Available Skills

| Skill | File | Description |
|---|---|---|
| State Machine | `godogen/state_machine.yaml` | GDScript state machine with transitions |
| Component | `godogen/component.yaml` | Reusable component with exports/signals |
| UI Screen | `godogen/ui_screen.yaml` | Control-based UI screen layout |
| Input Map | `godogen/input_map.yaml` | Input action wrapper and registration |
| Animation Tree | `godogen/animation_tree.yaml` | AnimationTree state machine setup |

## Usage

Skills are loaded automatically by `GodogenIntegrator` on startup.

To use a skill via CLI:

```bash
godot-agent skill run generate_state_machine \
  --arg class_name=PlayerStateMachine \
  --arg states='[{"name": "Idle"}, {"name": "Run"}]'
```

## Adding Custom Skills

1. Create a new `.yaml` file in `skills/godogen/`
2. Define `name`, `description`, `inputSchema`, and `template`
3. Restart the agent — it auto-discovers new skills

## Template Syntax

Templates use Jinja2 with these conventions:
- `{{ variable }}` — variable interpolation
- `{%- for item in items %}` — loops
- `{%- if condition %}` — conditionals
- `| indent(4)` — indent a block
- `| upper`, `| lower` — case transforms
