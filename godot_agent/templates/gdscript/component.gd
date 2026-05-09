class_name {{ class_name }} extends {{ extends | default("Node") }}

{% for sig in signals %}
signal {{ sig.name }}{% if sig.args %}({% for a in sig.args %}{{ a }}{% if not loop.last %}, {% endif %}{% endfor %}){% endif %}
{% endfor %}

{% for prop in properties %}
{% if prop.export %}
@export {% endif %}var {{ prop.name }}: {{ prop.type }} = {{ prop.default }}
{% endfor %}

func _ready() -> void:
	pass

func _process(delta: float) -> void:
	pass
