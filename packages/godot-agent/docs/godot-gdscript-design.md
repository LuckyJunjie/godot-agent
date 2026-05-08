# Godot Agent — GDScript Design Guidelines

## 1. Code Style (enforced by agent)

The agent follows and enforces the [GDScript style guide](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html) with these project-specific additions:

### 1.1 Naming

| Type | Convention | Example |
|---|---|---|
| Classes | PascalCase | `PlayerController`, `InventoryGrid` |
| Variables | snake_case | `max_health`, `is_jumping` |
| Constants | UPPER_SNAKE_CASE | `MAX_SPEED`, `DEFAULT_COLOR` |
| Signals | snake_case, past tense | `health_changed`, `item_picked_up` |
| Functions | snake_case, verb | `take_damage()`, `get_nearest_enemy()` |
| Private | leading underscore | `_calculate_path()` |

### 1.2 Type Hints

Always use static typing. The agent flags untyped variables as warnings.

```gdscript
# Good
var velocity: Vector2 = Vector2.ZERO
var health: int = 100
@onready var sprite: Sprite2D = $Sprite2D

# Bad
var velocity = Vector2.ZERO  # implicit OK, but prefer explicit
var health = 100             # ambiguous: int or float?
var node = $Sprite2D         # lost type information
```

### 1.3 Documentation Comments

Every public class, signal, and function must be documented:

```gdscript
class_name PlayerController
extends CharacterBody2D

## Emitted when health reaches zero.
signal died

## Current movement speed in pixels per second.
@export var speed: float = 300.0

## Applies damage and updates health. Emits [signal died] if health <= 0.
func take_damage(amount: int) -> void:
    health -= amount
    if health <= 0:
        died.emit()
```

The agent parses these comments to:
- Generate API docs.
- Validate signal connections.
- Provide better LLM context.

---

## 2. Design Patterns

### 2.1 State Machine

Use the built-in godogen skill for state machines:

```gdscript
class_name PlayerStateMachine extends Node

enum State { IDLE, RUN, JUMP, FALL, ATTACK }

var current: State = State.IDLE
var previous: State = State.IDLE

func transition_to(next: State) -> void:
    if not _can_transition(current, next):
        push_warning("Invalid transition: %s -> %s" % [current, next])
        return
    previous = current
    current = next
    _enter_state(current)
```

### 2.2 Component Pattern

```gdscript
# components/health_component.gd
class_name HealthComponent extends Node

signal health_changed(new: int, max: int)
signal died

@export var max_health: int = 100
var current: int = max_health

func take_damage(amount: int) -> void:
    current = clampi(current - amount, 0, max_health)
    health_changed.emit(current, max_health)
    if current == 0:
        died.emit()
```

Attach to any entity:
```gdscript
# In enemy.gd
@onready var health: HealthComponent = $HealthComponent
```

### 2.3 Observer / Event Bus

For decoupled communication, use an autoload event bus:

```gdscript
# autoload/event_bus.gd
extends Node

signal enemy_died(enemy: Node, position: Vector2)
signal coin_collected(value: int)
signal level_completed(level_id: String)
```

Publish:
```gdscript
EventBus.enemy_died.emit(self, global_position)
```

Subscribe:
```gdscript
EventBus.enemy_died.connect(_on_enemy_died)
```

The agent maintains a subscription map to detect orphaned connections.

### 2.4 Resource-Based Configuration

Use `.tres` files for tunable gameplay values:

```gdscript
# resources/player_stats.gd
class_name PlayerStats extends Resource

@export var speed: float = 300.0
@export var jump_force: float = 450.0
@export var gravity: float = 980.0
```

```gdscript
# player.gd
@export var stats: PlayerStats
```

Benefits:
- Designers can tweak values without touching code.
- The agent can generate balanced variants via LLM.

---

## 3. GDScript Edit Tool

### 3.1 API

```python
class GDScriptEditTool:
    def read(script_path: str) -> str
    def inspect(script_path: str) -> GDScriptModule
    
    def add_function(script_path: str, name: str, args: list, 
                     return_type: str, body: str) -> EditResult
    def add_signal(script_path: str, name: str, args: list) -> EditResult
    def add_export(script_path: str, name: str, type: str, 
                   default: Any | None) -> EditResult
    def edit_function_body(script_path: str, name: str, 
                           new_body: str) -> EditResult
    def rename_symbol(script_path: str, old: str, new: str) -> EditResult
```

### 3.2 AST Preservation

The agent uses a lightweight GDScript AST parser to:
- Insert new functions in logical order (signals → exports → onready → funcs).
- Preserve existing comments and formatting.
- Detect naming collisions before editing.

### 3.3 Example Interaction

```
User: Add a dodge roll to the player

Agent:
  1. gdscript_inspect("res://scripts/player.gd")
  2. gdscript_add_function(
       script_path="res://scripts/player.gd",
       name="dodge",
       args=[{"name": "direction", "type": "Vector2"}],
       return_type="void",
       body='''
         if not is_on_floor():
             return
         velocity = direction * DODGE_SPEED
         _is_dodging = true
         $DodgeTimer.start()
       '''
     )
  3. gdscript_add_export(
       script_path="res://scripts/player.gd",
       name="dodge_speed",
       type="float",
       default=600.0
     )
  4. scene_add_node(...)  # DodgeTimer
  5. harness_run_unit("res://tests/test_player.gd")
```

---

## 4. Anti-Patterns (flagged by agent)

| Anti-Pattern | Why | Fix |
|---|---|---|
| `get_node()` without `@onready` | Runtime errors, brittle | Use `@onready var x = $Path` |
| Deep node paths (`$"A/B/C/D"`) | Breaks on restructure | Export NodePaths or use groups |
| `process_delta` for timers | Frame-rate dependent | Use `Timer` or `get_tree().create_timer()` |
| Singleton abuse (>5 autoloads) | Hidden dependencies | Use dependency injection or event bus |
| Mixed responsibilities | Hard to test | Split into components |
| Unchecked `connect()` returns | Silent failures | Check return value or use `connect(...).is_ok()` |

---

## 5. Script Templates

The agent ships with templates in `godot_agent/templates/gdscript/`:

| Template | Use Case |
|---|---|
| `node2d` | Generic 2D node with _process |
| `character_body_2d` | Platformer/top-down controller |
| `area_2d` | Trigger / pickup |
| `resource` | Custom Resource class |
| `state` | State machine state |
| `component` | Reusable component |
| `autoload` | Singleton / manager |
| `test_gut` | GUT test case |
| `test_harness` | Scene harness test |

Template variables are filled via godogen:
```yaml
# skill invocation
generate_gdscript:
  template: character_body_2d
  class_name: PlayerController
  exports:
    - { name: speed, type: float, default: 300 }
```
