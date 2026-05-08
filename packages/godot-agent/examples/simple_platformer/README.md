# Simple Platformer Example

A minimal Godot 4.2 platformer project demonstrating godot-agent capabilities.

## Project Structure

```
simple_platformer/
├── project.godot          # Godot project settings
├── scenes/
│   ├── player.tscn        # Player character scene
│   └── level_01.tscn      # First level
├── scripts/
│   ├── player.gd          # Player controller
│   └── autoload/
│       ├── game_state.gd  # Global state
│       └── event_bus.gd   # Global signals
├── tests/
│   └── test_player.gd     # GUT tests
└── gdd/
    └── stories/
        └── story-001-player-movement.md
```

## Using godot-agent

```bash
# Inspect the project
godot-agent inspect --project examples/simple_platformer

# Validate GDD traceability
godot-agent gdd-validate --project examples/simple_platformer

# Run tests
godot-agent harness --project examples/simple_platformer res://tests/test_player.gd
```
