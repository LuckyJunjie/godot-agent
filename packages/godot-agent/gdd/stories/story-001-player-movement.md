---
id: story-001
title: Player Movement
status: implemented
scenes:
  - res://scenes/entities/player.tscn
  - res://scenes/levels/test_level.tscn
scripts:
  - res://scripts/player.gd
  - res://scripts/components/movement_component.gd
tests:
  - res://tests/unit/test_player_movement.gd
  - res://tests/harness/test_player_scene.gd
acceptance:
  - Player can move with WASD or arrow keys
  - Player collision respects tilemap boundaries
  - Player can jump with Space (single and double jump)
  - Player sprite flips based on movement direction
  - Movement feels responsive with configurable speed and acceleration
---

# Story 001: Player Movement

## Overview

The player character must be able to navigate the 2D game world using standard platformer controls.

## Mechanics

### Basic Movement
- **Walk**: Horizontal input (A/D or Left/Right arrows)
- **Jump**: Spacebar or gamepad button A
- **Double Jump**: Press jump again while in mid-air (once per air time)
- **Crouch**: Hold S or Down arrow (reduces hitbox, slower movement)

### Physics Parameters
| Parameter | Value | Description |
|---|---|---|
| `speed` | 300.0 | Max horizontal speed (px/s) |
| `acceleration` | 1200.0 | Ground acceleration (px/s²) |
| `air_acceleration` | 600.0 | Air acceleration (px/s²) |
| `friction` | 800.0 | Ground friction (px/s²) |
| `jump_force` | 450.0 | Initial jump velocity (px/s) |
| `gravity` | 980.0 | Gravity scale (px/s²) |
| `coyote_time` | 0.1 | Grace period for jumping after leaving ground (s) |
| `jump_buffer` | 0.1 | Input buffer for early jump press (s) |

## Implementation Notes

- Uses `CharacterBody2D` with `move_and_slide()`
- Movement logic extracted to `MovementComponent` for reusability
- Input handling centralized in `InputMap` via autoload
- Animations driven by `AnimationTree` state machine
