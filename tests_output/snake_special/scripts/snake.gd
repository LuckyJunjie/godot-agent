extends Node2D
class_name NeonSnake

var speed: float = 200.0
var direction: Vector2 = Vector2.RIGHT
var body: Array = []
var score: int = 0
var game_over: bool = false
var can_wrap: bool = true
var wraps: int = 3
var food: Vector2

func _ready():
    for i in range(5):
        var r = ColorRect.new()
        r.size = Vector2(20, 20)
        r.position = Vector2(400 - i * 20, 300)
        r.color = Color(0, 1, 0.5)
        add_child(r)
        body.append(r)
    spawn_food()

func _process(delta):
    if game_over: return
    var head = body[0]
    var new_pos = head.position + direction * speed * delta
    if can_wrap and wraps > 0:
        var ss = get_viewport_rect().size
        if new_pos.x < 0: new_pos.x = ss.x; wraps -= 1
        elif new_pos.x > ss.x: new_pos.x = 0; wraps -= 1
        if new_pos.y < 0: new_pos.y = ss.y; wraps -= 1
        elif new_pos.y > ss.y: new_pos.y = 0; wraps -= 1
    for i in range(body.size() - 1, 0, -1):
        body[i].position = body[i-1].position
    body[0].position = new_pos

func spawn_food():
    var ss = get_viewport_rect().size
    food = Vector2(randf() * (ss.x - 40) + 20, randf() * (ss.y - 40) + 20)

func _input(e):
    if e.is_action_pressed("ui_up"): direction = Vector2.UP
    elif e.is_action_pressed("ui_down"): direction = Vector2.DOWN
    elif e.is_action_pressed("ui_left"): direction = Vector2.LEFT
    elif e.is_action_pressed("ui_right"): direction = Vector2.RIGHT
