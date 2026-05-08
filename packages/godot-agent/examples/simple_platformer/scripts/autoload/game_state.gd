extends Node

## Global game state singleton.

var score: int = 0
var lives: int = 3
var current_level: int = 1

func _ready() -> void:
	pass

func add_score(points: int) -> void:
	score += points

func lose_life() -> void:
	lives -= 1
	if lives <= 0:
		_game_over()

func _game_over() -> void:
	# TODO: implement game over screen
	pass
