extends Node

## Global event bus for decoupled communication.

signal coin_collected(value: int)
signal enemy_defeated(enemy: Node, position: Vector2)
signal player_died
signal level_completed(level_id: int)
