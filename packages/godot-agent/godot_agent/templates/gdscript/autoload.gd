extends Node

## {{ class_name }}
## Autoload singleton for {{ purpose | default("global game state") }}.

{% for prop in properties %}
var {{ prop.name }}: {{ prop.type }} = {{ prop.default }}
{% endfor %}

func _ready() -> void:
	pass

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		_save_state()

func _save_state() -> void:
	# TODO: persist state
	pass
