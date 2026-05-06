#encoding: utf-8
extends Node2D

class_name Snake

# Properties
var speed: float = 200.0
var direction: Vector2 = Vector2.RIGHT
var body_parts: Array = []
var can_wrap: bool = true
var wrap_charges: int = 3

# Food
var food_position: Vector2

# Game state
var score: int = 0
var is_game_over: bool = false

func _ready():
    # Initialize snake body
    var start_pos = get_viewport_rect().size / 2
    for i in range(5):
        add_body_part(start_pos - Vector2(i * 20, 0))
    
    # Spawn first food
    spawn_food()

func _process(delta):
    if is_game_over:
        return
    
    # Move snake
    move_snake(delta)
    
    # Check food collision
    check_food_collision()
    
    # Check wall collision
    check_wall_collision()

func move_snake(delta):
    var head = body_parts[0]
    var new_pos = head.position + direction * speed * delta
    
    # Wrap around screen or stop?
    if can_wrap and wrap_charges > 0:
        wrap_position(new_pos)
    
    # Move body parts
    for i in range(body_parts.size() - 1, 0, -1):
        body_parts[i].position = body_parts[i-1].position
    
    if body_parts.size() > 0:
        body_parts[0].position = new_pos

func add_body_part(position: Vector2):
    var part = ColorRect.new()
    part.size = Vector2(20, 20)
    part.position = position
    part.color = Color(0, 1, 0.5)  # Neon green
    
    # Add glow effect
    var mat = StandardMaterial3D.new()
    mat.emission_enabled = true
    mat.emission = Color(0, 1, 0.5)
    mat.emission_energy = 2.0
    
    add_child(part)
    body_parts.append(part)

func spawn_food():
    var screen_size = get_viewport_rect().size
    food_position = Vector2(
        randf() * (screen_size.x - 40) + 20,
        randf() * (screen_size.y - 40) + 20
    )

func check_food_collision():
    var head = body_parts[0]
    if head.position.distance_to(food_position) < 25:
        score += 10
        add_body_part(body_parts[-1].position)
        spawn_food()

func wrap_position(pos: Vector2):
    var screen_size = get_viewport_rect().size
    
    if pos.x < 0:
        pos.x = screen_size.x
        wrap_charges -= 1
    elif pos.x > screen_size.x:
        pos.x = 0
        wrap_charges -= 1
    elif pos.y < 0:
        pos.y = screen_size.y
        wrap_charges -= 1
    elif pos.y > screen_size.y:
        pos.y = 0
        wrap_charges -= 1

func check_wall_collision():
    var head = body_parts[0]
    var screen_size = get_viewport_rect().size
    
    if head.position.x < 0 or head.position.x > screen_size.x:
        if not can_wrap or wrap_charges <= 0:
            game_over()
    elif head.position.y < 0 or head.position.y > screen_size.y:
        if not can_wrap or wrap_charges <= 0:
            game_over()

func game_over():
    is_game_over = true
    print("Game Over! Score: ", score)

func _input(event):
    if event is InputEventKey and event.pressed:
        match event.keycode:
            KEY_UP, KEY_W:
                direction = Vector2.UP
            KEY_DOWN, KEY_S:
                direction = Vector2.DOWN
            KEY_LEFT, KEY_A:
                direction = Vector2.LEFT
            KEY_RIGHT, KEY_D:
                direction = Vector2.RIGHT
            KEY_SPACE:
                if can_wrap and wrap_charges > 0:
                    wrap_charges -= 1