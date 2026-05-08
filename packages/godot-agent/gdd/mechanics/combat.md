---
id: mechanic-combat
title: Combat System
status: draft
scenes:
  - res://scenes/entities/player.tscn
  - res://scenes/entities/enemy_base.tscn
scripts:
  - res://scripts/components/health_component.gd
  - res://scripts/components/hitbox_component.gd
---

# Combat System

## Overview

A simple real-time combat system with health, damage, and hit detection.

## Components

### HealthComponent
- Tracks current and max health
- Emits `health_changed` and `died` signals
- Supports damage, heal, and invulnerability frames

### HitboxComponent
- Defines attack shape (Area2D)
- Configurable damage, knockback, and hit stun
- Layer/mask based collision filtering

## Damage Formula

```
damage = base_damage * attacker_multiplier - defender_defense
```

## Future Extensions
- Combo system
- Elemental damage types
- Status effects (poison, stun, freeze)
