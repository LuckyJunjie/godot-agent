#encoding: utf-8
extends Node2D

class_name Snake

var speed: float = 200.0
var direction: Vector2 = Vector2.RIGHT
var body_parts: Array = []
var score: int = 0
var is_game_over: bool = false
var can_wrap: bool = true
var wrap_charges: int = 3

func _ready():
    pass

func _physics_process(delta):
    if is_game_over:
        return

func move_snake(delta):
    pass

func _input(event):
    if event.is_action_pressed("ui_up"):
        direction = Vector2.UP
    elif event.is_action_pressed("ui_down"):
        direction = Vector2.DOWN
    elif event.is_action_pressed("ui_left"):
        direction = Vector2.LEFT
    elif event.is_action_pressed("ui_right"):
        direction = Vector2.RIGHT

func game_over():
    is_game_over = true
    print("Game Over! Score: ", score)
