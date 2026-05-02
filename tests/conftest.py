"""
pytest configuration and fixtures for godot-agent.
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def sample_tscn():
    """Sample .tscn content."""
    return """[gd_scene load_steps=2 format=3]

[ext_resource path="res://player.tscn" type="PackedScene" id=1]

[node name="Main" type="Node2D"]
[node name="Player" type="CharacterBody2D" parent="."]
[node name="Sprite" type="Sprite2D" parent="Player"]
[node name="Collision" type="CollisionShape2D" parent="Player"]
"""


@pytest.fixture
def sample_tres():
    """Sample .tres content."""
    return """[gd_resource type="Resource" load_steps=2 format=3]

[resource]
resource_name = "PlayerData"
health = 100
speed = 200.0
"""


@pytest.fixture
def sample_gdscript():
    """Sample GDScript content."""
    return """
extends CharacterBody2D

@export var health: int = 100
@export var speed: float = 200.0

func _ready():
    print("Player ready")

func _physics_process(delta):
    move_and_slide()
"""


@pytest.fixture
def project_with_scene(temp_project, sample_tscn):
    """Project with a sample scene file."""
    scene_file = temp_project / "player.tscn"
    scene_file.write_text(sample_tscn)
    return temp_project


@pytest.fixture
def project_with_gdd(temp_project):
    """Project with GDD initialized."""
    from godot_agent.gdd import GDDEngine
    engine = GDDEngine(str(temp_project))
    engine.initialize()
    return temp_project


@pytest.fixture
def project_with_assets(temp_project):
    """Project with assets directory."""
    from godot_agent.assets import AssetPipeline
    pipeline = AssetPipeline(str(temp_project))
    pipeline.initialize()
    return temp_project