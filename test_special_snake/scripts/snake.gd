#encoding: utf-8
extends Node2D
class_name NeonSnake

var speed: float = 200.0
var direction: Vector2 = Vector2.RIGHT
var body_parts: Array = []
var score: int = 0
var is_game_over: bool = false
var can_wrap: bool = true
var wrap_charges: int = 3
var food_pos: Vector2
var boost_active: bool = false

func _ready():
    var start = get_viewport_rect().size / 2
    for i in range(5):
        add_body(start - Vector2(i * 20, 0))
    spawn_food()

func _process(delta):
    if is_game_over: return
    var head = body_parts[0]
    var new_pos = head.position + direction * (speed * (1.5 if boost_active else 1.0)) * delta
    if can_wrap and wrap_charges > 0: wrap_pos(new_pos)
    for i in range(body_parts.size() - 1, 0, -1):
        body_parts[i].position = body_parts[i-1].position
    body_parts[0].position = new_pos
    check_food()
    check_walls()

func add_body(pos: Vector2):
    var part = ColorRect.new()
    part.size = Vector2(20, 20)
    part.position = pos
    part.color = Color(0.2, 1.0, 0.5) if boost_active else Color(0, 1, 0.5)
    add_child(part); body_parts.append(part)

func spawn_food():
    var sz = get_viewport_rect().size
    food_pos = Vector2(randf() * (sz.x - 40) + 20, randf() * (sz.y - 40) + 20)

func check_food():
    if body_parts[0].position.distance_to(food_pos) < 25:
        score += 10
        add_body(body_parts[-1].position)
        spawn_food()

func wrap_pos(pos: Vector2):
    var sz = get_viewport_rect().size
    if pos.x < 0: pos.x = sz.x; wrap_charges -= 1
    elif pos.x > sz.x: pos.x = 0; wrap_charges -= 1
    elif pos.y < 0: pos.y = sz.y; wrap_charges -= 1
    elif pos.y > sz.y: pos.y = 0; wrap_charges -= 1

func check_walls():
    var head = body_parts[0]
    var sz = get_viewport_rect().size
    if head.position.x < 0 or head.position.x > sz.x or head.position.y < 0 or head.position.y > sz.y:
        if not can_wrap or wrap_charges <= 0: game_over()

func game_over(): is_game_over = true; print("Game Over! Score: ", score)

func _input(event):
    if event.is_action_pressed("ui_up"): direction = Vector2.UP
    elif event.is_action_pressed("ui_down"): direction = Vector2.DOWN
    elif event.is_action_pressed("ui_left"): direction = Vector2.LEFT
    elif event.is_action_pressed("ui_right"): direction = Vector2.RIGHT
    elif event.is_action_pressed("ui_accept"): boost_active = not boost_active
    elif event.is_action_pressed("ui_cancel") and can_wrap and wrap_charges > 0:
        wrap_charges -= 1






