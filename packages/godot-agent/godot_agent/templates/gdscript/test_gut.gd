extends GutTest

var {{ class_under_test }} = load("res://{{ script_path }}")

func before_each() -> void:
	# Setup before each test
	pass

func after_each() -> void:
	# Cleanup after each test
	pass

func test_can_instantiate() -> void:
	var instance = {{ class_under_test }}.new()
	assert_not_null(instance)
	instance.free()

func test_default_values() -> void:
	var instance = {{ class_under_test }}.new()
	# TODO: assert default property values
	instance.free()
