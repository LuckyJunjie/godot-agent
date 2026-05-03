class_name Player extends CharacterBody2D

## Emitted when player health changes.
signal health_changed(new_health: int, max_health: int)
## Emitted when player dies.
signal died

@export var speed: float = 300.0
@export var jump_force: float = 450.0
@export var gravity: float = 980.0
@export var max_health: int = 100

@onready var sprite: Sprite2D = $Sprite2D
@onready var animation_player: AnimationPlayer = $AnimationPlayer
@onready var coyote_timer: Timer = $CoyoteTimer

var current_health: int = max_health
var can_double_jump: bool = true

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
	var direction := Input.get_axis("move_left", "move_right")
	velocity.x = direction * speed
	
	if direction != 0:
		sprite.flip_h = direction < 0
	
	if Input.is_action_just_pressed("jump"):
		_try_jump()

func _handle_movement(delta: float) -> void:
	pass  # velocity set in _handle_input

func _handle_animation() -> void:
	if animation_player == null:
		return
	if not is_on_floor():
		animation_player.play("jump")
	elif velocity.x != 0:
		animation_player.play("run")
	else:
		animation_player.play("idle")

func _try_jump() -> void:
	if is_on_floor() or not coyote_timer.is_stopped():
		velocity.y = -jump_force
		coyote_timer.stop()
		can_double_jump = true
	elif can_double_jump:
		velocity.y = -jump_force
		can_double_jump = false

func take_damage(amount: int) -> void:
	current_health = clampi(current_health - amount, 0, max_health)
	health_changed.emit(current_health, max_health)
	if current_health == 0:
		died.emit()

func heal(amount: int) -> void:
	current_health = clampi(current_health + amount, 0, max_health)
	health_changed.emit(current_health, max_health)
