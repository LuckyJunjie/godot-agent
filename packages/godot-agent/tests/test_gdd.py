"""Tests for GDD module."""

import pytest
from godot_agent.gdd import GDDEngine, GDDStory


class TestGDDStory:
    """Tests for GDDStory class."""
    
    def test_create_story(self):
        """Test creating a story."""
        story = GDDStory(id="001", title="Player Movement")
        assert story.id == "001"
        assert story.title == "Player Movement"
        assert story.status == "draft"
        assert story.scenes == []
        assert story.scripts == []
        assert story.tests == []
        assert story.acceptance == []
    
    def test_story_with_data(self):
        """Test creating a story with data."""
        story = GDDStory(
            id="002",
            title="Inventory",
            status="approved",
            scenes=["player.tscn"],
            scripts=["player.gd"],
            tests=["test_player.gd"],
            acceptance=["Can pick up items"]
        )
        assert story.status == "approved"
        assert len(story.scenes) == 1
        assert len(story.acceptance) == 1


class TestGDDEngine:
    """Tests for GDDEngine class."""
    
    def test_create_engine(self, temp_project):
        """Test creating a GDD engine."""
        engine = GDDEngine(str(temp_project))
        assert engine.project_root == temp_project
    
    def test_initialize(self, temp_project):
        """Test initializing GDD directories."""
        engine = GDDEngine(str(temp_project))
        engine.initialize()
        
        assert (temp_project / "gdd").exists()
        assert (temp_project / "gdd" / "stories").exists()
        assert (temp_project / "gdd" / "mechanics").exists()
        assert (temp_project / "gdd" / "world").exists()
        assert (temp_project / "gdd" / "assets").exists()
        assert (temp_project / "gdd" / "index.md").exists()
    
    def test_load_stories_empty(self, project_with_gdd):
        """Test loading stories from empty directory."""
        from godot_agent.gdd import GDDEngine
        engine = GDDEngine(str(project_with_gdd))
        stories = engine.load_stories()
        assert stories == []
    
    def test_create_story(self, project_with_gdd):
        """Test creating a new story."""
        from godot_agent.gdd import GDDEngine
        engine = GDDEngine(str(project_with_gdd))
        
        story = engine.create_story(
            story_id="001",
            title="Player Movement",
            content="Player can move with WASD"
        )
        
        assert story.id == "001"
        assert story.title == "Player Movement"
        
        # Check file was created
        story_file = project_with_gdd / "gdd" / "stories" / "story-001.md"
        assert story_file.exists()
    
    def test_update_story(self, project_with_gdd):
        """Test updating a story."""
        from godot_agent.gdd import GDDEngine
        engine = GDDEngine(str(project_with_gdd))
        
        # Create story first
        engine.create_story("001", "Player Movement", "Content")
        
        # Update
        engine.update_story("001", status="approved")
        
        # Verify update
        stories = engine.load_stories()
        assert len(stories) == 1
        assert stories[0].status == "approved"
    
    def test_validate_traceability_empty(self, project_with_gdd):
        """Test validating with no references."""
        from godot_agent.gdd import GDDEngine
        engine = GDDEngine(str(project_with_gdd))
        result = engine.validate_traceability()
        
        assert result["valid"] is True
        assert result["issues"] == []
    
    def test_get_index(self, project_with_gdd):
        """Test getting GDD index."""
        from godot_agent.gdd import GDDEngine
        engine = GDDEngine(str(project_with_gdd))
        engine.initialize()
        
        index = engine.get_index()
        assert "project" in index