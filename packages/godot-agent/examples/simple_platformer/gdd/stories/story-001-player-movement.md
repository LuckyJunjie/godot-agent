---
id: story-001
title: Player Movement
status: implemented
scenes:
  - res://scenes/player.tscn
  - res://scenes/level_01.tscn
scripts:
  - res://scripts/player.gd
tests:
  - res://tests/test_player.gd
acceptance:
  - Player moves with A/D keys
  - Player jumps with Space
  - Player has double jump
  - Player sprite flips with direction
---

# Story 001: Player Movement

Basic platformer movement with walk, jump, and double jump.
