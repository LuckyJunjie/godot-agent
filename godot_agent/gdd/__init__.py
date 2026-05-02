"""
GDD Engine
Manages Game Design Document as structured memory.
"""

from pathlib import Path
from typing import Optional
import yaml
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GDDStory:
    """A story in the GDD."""
    id: str
    title: str
    status: str = "draft"  # draft, approved, implemented, deprecated
    scenes: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)
    content: str = ""


class GDDEngine:
    """Manages GDD storage and synchronization."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.gdd_dir = self.project_root / "gdd"
        self.stories_dir = self.gdd_dir / "stories"
        self.mechanics_dir = self.gdd_dir / "mechanics"
        self.world_dir = self.gdd_dir / "world"
        self.assets_dir = self.gdd_dir / "assets"
    
    def initialize(self):
        """Create GDD directory structure."""
        for d in [self.gdd_dir, self.stories_dir, self.mechanics_dir, 
                  self.world_dir, self.assets_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Create index.md if not exists
        index_file = self.gdd_dir / "index.md"
        if not index_file.exists():
            index_file.write_text(self._default_index())
    
    def _default_index(self) -> str:
        """Default GDD index."""
        return """---
project: Godot Agent Project
version: 0.1.0
created: {date}
---

# Game Design Document

## Stories

* [Story 001: Player Movement](stories/story-001-player-movement.md)

## Mechanics

## World

## Assets

## Style Guide

""".format(date=datetime.now().strftime("%Y-%m-%d"))
    
    def load_stories(self) -> list[GDDStory]:
        """Load all stories."""
        stories = []
        
        for story_file in self.stories_dir.glob("*.md"):
            story = self._parse_story(story_file)
            if story:
                stories.append(story)
        
        return stories
    
    def _parse_story(self, path: Path) -> Optional[GDDStory]:
        """Parse a story file."""
        content = path.read_text()
        
        # Extract front-matter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                front_matter = yaml.safe_load(parts[1])
                story = GDDStory(
                    id=front_matter.get("id", ""),
                    title=front_matter.get("title", ""),
                    status=front_matter.get("status", "draft"),
                    scenes=front_matter.get("scenes", []),
                    scripts=front_matter.get("scripts", []),
                    tests=front_matter.get("tests", []),
                    acceptance=front_matter.get("acceptance", []),
                    content=parts[2].strip() if len(parts) > 2 else ""
                )
                return story
        
        return None
    
    def create_story(self, story_id: str, title: str, content: str = "") -> GDDStory:
        """Create a new story."""
        story = GDDStory(id=story_id, title=title, content=content)
        
        # Write to file
        story_file = self.stories_dir / f"story-{story_id}.md"
        story_file.write_text(self._story_to_markdown(story))
        
        return story
    
    def _story_to_markdown(self, story: GDDStory) -> str:
        """Convert story to markdown with front-matter."""
        front_matter = {
            "id": story.id,
            "title": story.title,
            "status": story.status,
            "scenes": story.scenes,
            "scripts": story.scripts,
            "tests": story.tests,
            "acceptance": story.acceptance,
        }
        
        lines = ["---", yaml.dump(front_matter), "---", "", story.content]
        return "\n".join(lines)
    
    def update_story(self, story_id: str, **kwargs):
        """Update story fields."""
        story_file = self.stories_dir / f"story-{story_id}.md"
        
        if story_file.exists():
            story = self._parse_story(story_file)
            if story:
                for key, value in kwargs.items():
                    if hasattr(story, key):
                        setattr(story, key, value)
                
                story_file.write_text(self._story_to_markdown(story))
    
    def validate_traceability(self) -> dict:
        """Validate that all referenced files exist."""
        stories = self.load_stories()
        issues = []
        
        for story in stories:
            for scene in story.scenes:
                if not (self.project_root / scene).exists():
                    issues.append(f"Missing scene: {scene}")
            
            for script in story.scripts:
                if not (self.project_root / script).exists():
                    issues.append(f"Missing script: {script}")
            
            for test in story.tests:
                if not (self.project_root / test).exists():
                    issues.append(f"Missing test: {test}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def get_index(self) -> dict:
        """Get GDD index metadata."""
        index_file = self.gdd_dir / "index.md"
        
        if not index_file.exists():
            return {}
        
        content = index_file.read_text()
        
        # Parse front-matter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                return yaml.safe_load(parts[1]) or {}
        
        return {}