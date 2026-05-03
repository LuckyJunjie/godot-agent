# Godot Agent — Scenes Structure & Design

## 1. Scene Philosophy

In Godot, scenes are the primary organizational unit. The Godot Agent treats scenes as **first-class code artifacts**:
- Every scene has a design spec in the GDD.
- Every scene change is validated by the harness.
- Scene diffs are presented to the user in human-readable format.

---

## 2. Recommended Project Structure

```
my_game/
├── project.godot
├── gdd/
│   └── ...
├── scenes/
│   ├── autoload/           # Singletons (globals, audio, input)
│   ├── ui/                 # Menus, HUD, dialogs
│   ├── levels/             # Gameplay levels/worlds
│   ├── entities/           # Player, enemies, NPCs
│   ├── components/         # Reusable scene components
│   └── effects/            # Particles, shaders, animations
├── scripts/
│   ├── autoload/
│   ├── entities/
│   ├── components/
│   └── utils/
├── assets/
│   ├── sprites/
│   ├── audio/
│   ├── fonts/
│   └── tilesets/
└── tests/
    ├── unit/
    └── harness/
```

---

## 3. Scene Design Patterns

### 3.1 Composition over Inheritance

Prefer composing scenes from smaller scene instances rather than deep inheritance chains.

```
Player (Node2D)
├── Sprite2D
├── HealthComponent (instance of components/health.tscn)
├── MovementComponent (instance of components/movement.tscn)
└── StateMachine (instance of components/state_machine.tscn)
```

Agent tooling enforces this by:
- Flagging inheritance depths > 3 as a lint warning.
- Suggesting component extraction when a scene exceeds 15 nodes.

### 3.2 Scene Contracts

Every scene declares its public interface in a header comment:

```gdscript
# scene: res://scenes/entities/player.tscn
# exports:
#   speed: float — pixels per second
#   max_health: int
# signals:
#   health_changed(new: int, max: int)
#   died()
# groups:
#   player, damageable
```

The agent parses these contracts to:
- Validate connections in parent scenes.
- Auto-complete signal names in other scripts.
- Detect breaking changes across scene boundaries.

### 3.3 Autoload Registry

Autoloads are global. The agent maintains an index:

```yaml
# autoloads.yml
GameState:
  path: res://scenes/autoload/game_state.tscn
  responsibilities: ["save/load", "settings", "player progress"]
AudioManager:
  path: res://scenes/autoload/audio_manager.tscn
  responsibilities: ["music", "sfx", "bus mixing"]
```

This prevents circular dependencies and documents global state.

---

## 4. Scene Edit Tool

### 4.1 API

```python
class SceneEditTool:
    """Native tool for safe scene editing."""
    
    def read(scene_path: str) -> str
    def inspect(scene_path: str) -> SceneGraph
    
    def add_node(scene_path: str, parent: str, name: str, type: str, 
                 properties: dict | None = None) -> EditResult
    def remove_node(scene_path: str, node_path: str) -> EditResult
    def set_property(scene_path: str, node_path: str, key: str, value: Any) -> EditResult
    def add_signal(scene_path: str, from_path: str, signal: str, 
                   to_path: str, method: str, binds: list | None = None) -> EditResult
    def set_script(scene_path: str, node_path: str, script_path: str) -> EditResult
    
    def batch_edit(scene_path: str, edits: list[EditOp]) -> EditResult
```

### 4.2 Safety Guarantees

- **Type validation**: `set_property` checks the value against Godot's ClassDB.
- **Reference integrity**: Removing a node warns about broken signal connections.
- **Backup**: Every edit creates a `.tscn.bak` before writing.
- **Sandbox**: Edits are rejected if `scene_path` is outside `projectPath`.

### 4.3 Example Interaction

```
User: Add a health bar above the player

Agent:
  1. scene_inspect("res://scenes/entities/player.tscn")
  2. scene_add_node(
       scene_path="res://scenes/entities/player.tscn",
       parent=".",
       name="HealthBar",
       type="TextureProgressBar",
       properties={
         "layout_mode": 1,
         "anchors_preset": 5,
         "offset_top": -20,
         "value": 100
       }
     )
  3. scene_add_signal(
       scene_path="res://scenes/entities/player.tscn",
       from_path="HealthComponent",
       signal="health_changed",
       to_path="HealthBar",
       method="set_value"
     )
  4. harness_run_scene("res://scenes/entities/player.tscn")
```

---

## 5. Scene Generation from GDD

### 5.1 Story-to-Scene Mapping

A GDD story can trigger automatic scene generation:

```yaml
---
id: story-003
status: approved
generate:
  scene: res://scenes/ui/inventory_grid.tscn
  from_template: grid_container_ui
  with:
    columns: 6
    slot_scene: res://scenes/ui/inventory_slot.tscn
---
```

The agent:
1. Loads the `grid_container_ui` godogen skill.
2. Generates the scene and associated script.
3. Runs harness to verify it instantiates without errors.
4. Updates story status to `implemented`.

### 5.2 Scene Templates

Built-in templates in `godot_agent/templates/scenes/`:

| Template | Description |
|---|---|
| `character_2d` | KinematicBody2D + Sprite + AnimationPlayer |
| `character_3d` | CharacterBody3D + MeshInstance + CollisionShape |
| `ui_screen` | Control root + CenterContainer + Panel |
| `level_2d` | Node2D + TileMap + ParallaxBackground |
| `autoload` | Node singleton with ready() setup |

---

## 6. Scene Versioning & Diff

Scenes are text files. The agent leverages this:

```bash
# Show what changed in a scene
godot-agent scene diff res://scenes/player.tscn --last

# Review before applying agent edits
godot-agent scene preview --patch player.patch.tscn
```

Diff format:
```diff
 [node name="HealthBar" type="TextureProgressBar" parent="."]
+layout_mode = 1
+anchors_preset = 5
+offset_top = -20.0
+value = 100.0
+texture_progress = ExtResource("2_abc123")
```
