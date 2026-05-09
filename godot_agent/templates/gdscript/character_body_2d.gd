class_name {{ class_name }} extends CharacterBody2D

@export var speed: float = 300.0
@export var jump_force: float = 450.0
@export var gravity: float = 980.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var animation_player: AnimationPlayer = $AnimationPlayer

var direction: float = 0.0

func _physics_process(delta: float) -> void:
	_apply_gravity(delta)
	_handle_input()
	_handle_movement(delta)
	_handle_animation()
	move_and_slide()

func _apply_gravity(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta

func _handle_input() -> void:
	direction = Input.get_axis("ui_left", "ui_right")
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		_jump()

func _handle_movement(delta: float) -> void:
	velocity.x = direction * speed
	if direction != 0:
		sprite.flip_h = direction < 0

func _handle_animation() -> void:
	if animation_player == null:
		return
	if not is_on_floor():
		animation_player.play("jump")
	elif direction != 0:
		animation_player.play("run")
	else:
		animation_player.play("idle")

func _jump() -> void:
	velocity.y = -jump_force

func take_damage(amount: int) -> void:
	# TODO: implement damage logic
	pass
