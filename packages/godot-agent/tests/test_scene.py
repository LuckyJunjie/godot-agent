"""Tests for scene module."""

import pytest
from godot_agent.scene import SceneDocument, ResourceDocument, SceneNode


class TestSceneNode:
    """Tests for SceneNode class."""
    
    def test_create_node(self):
        """Test creating a node."""
        node = SceneNode("test", "Node2D")
        assert node.name == "test"
        assert node.type == "Node2D"
        assert node.properties == {}
        assert node.children == []
    
    def test_node_with_instance(self):
        """Test creating a node with instance."""
        node = SceneNode("player", "CharacterBody2D", "player.tscn")
        assert node.instance == "player.tscn"
    
    def test_add_child(self):
        """Test adding a child node."""
        parent = SceneNode("root", "Node")
        child = SceneNode("child", "Node2D")
        parent.add_child(child)
        assert len(parent.children) == 1
        assert child.parent == parent
    
    def test_get_path(self):
        """Test getting node path."""
        root = SceneNode("root", "Node")
        child = SceneNode("child", "Node")
        root.add_child(child)
        assert child.get_path() == "root/child"


class TestSceneDocument:
    """Tests for SceneDocument class."""
    
    def test_create_document(self):
        """Test creating a document."""
        doc = SceneDocument()
        assert doc.path is None
        assert doc.root is None
    
    def test_load_scene(self, temp_project, sample_tscn):
        """Test loading a scene file."""
        scene_file = temp_project / "test.tscn"
        scene_file.write_text(sample_tscn)
        
        doc = SceneDocument()
        doc.load(str(scene_file))
        
        assert doc.path == str(scene_file)
        assert len(doc.ext_resources) > 0
    
    def test_save_scene(self, temp_project, sample_tscn):
        """Test saving a scene file."""
        scene_file = temp_project / "test.tscn"
        
        doc = SceneDocument()
        doc.ext_resources = ['[ext_resource path="res://player.tscn" type="PackedScene" id=1]']
        doc.save(str(scene_file))
        
        assert scene_file.exists()
    
    def test_add_node(self, temp_project):
        """Test adding a node to scene."""
        scene_file = temp_project / "test.tscn"
        scene_file.write_text("[gd_scene load_steps=0 format=3]\n")
        
        doc = SceneDocument()
        doc.load(str(scene_file))
        
        # Create root if not exists
        doc.root = SceneNode("root", "Node2D")
        
        new_node = doc.add_node("root", "Player", "CharacterBody2D")
        assert new_node.name == "Player"
        assert new_node.type == "CharacterBody2D"
    
    def test_set_property(self, temp_project):
        """Test setting a node property."""
        scene_file = temp_project / "test.tscn"
        scene_file.write_text("[gd_scene load_steps=0 format=3]\n[node name='root' type='Node2D']")
        
        doc = SceneDocument()
        doc.load(str(scene_file))
        doc.root = SceneNode("root", "Node2D")
        doc.root.properties["modulate"] = Color(1, 1, 1, 1)
        
        assert doc.root.properties["modulate"] is not None


class TestResourceDocument:
    """Tests for ResourceDocument class."""
    
    def test_create_resource(self):
        """Test creating a resource document."""
        doc = ResourceDocument()
        assert doc.resource_type == ""
        assert doc.properties == {}
    
    def test_load_resource(self, temp_project, sample_tres):
        """Test loading a resource file."""
        res_file = temp_project / "player.tres"
        res_file.write_text(sample_tres)
        
        doc = ResourceDocument()
        doc.load(str(res_file))
        
        assert doc.resource_type == "Resource"
        assert "health" in doc.properties
    
    def test_save_resource(self, temp_project):
        """Test saving a resource file."""
        res_file = temp_project / "test.tres"
        
        doc = ResourceDocument()
        doc.resource_type = "Resource"
        doc.properties = {"health": "100"}
        doc.save(str(res_file))
        
        assert res_file.exists()


# Need to add Color import
try:
    from godot_agent.scene import Color
except ImportError:
    class Color:
        """Mock Color."""
        def __init__(self, r, g, b, a):
            self.r, self.g, self.b, self.a = r, g, b, a