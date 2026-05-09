extends GutTest

var Player = load("res://scripts/player.gd")

func test_can_instantiate() -> void:
	var player = Player.new()
	assert_not_null(player)
	player.free()

func test_default_health() -> void:
	var player = Player.new()
	assert_eq(player.current_health, player.max_health)
	player.free()

func test_take_damage() -> void:
	var player = Player.new()
	player.take_damage(25)
	assert_eq(player.current_health, 75)
	player.free()

func test_heal() -> void:
	var player = Player.new()
	player.take_damage(50)
	player.heal(20)
	assert_eq(player.current_health, 70)
	player.free()
