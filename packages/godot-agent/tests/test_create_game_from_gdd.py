"""Tests for CreateGameFromGDDTool."""

import pytest
from pathlib import Path

from godot_agent.bridge.tools_compound import CreateGameFromGDDTool
from godot_agent.bridge.tools_gdd import GDDCreateTool
from godot_agent.gdd import GDDEngine


class TestCreateGameFromGDDTool:
    async def test_story_not_found(self, temp_project):
        tool = CreateGameFromGDDTool()
        result = await tool.execute(project_root=str(temp_project), story_id="999")
        assert "not found" in result

    async def test_create_game_from_gdd(self, temp_project):
        # First create a GDD story
        gdd_tool = GDDCreateTool()
        await gdd_tool.execute(
            project_root=str(temp_project),
            story_id="001",
            title="Test Game",
            content="A simple test game",
            scenes=["res://scenes/player.tscn", "res://scenes/enemy.tscn"],
            scripts=["res://scripts/player.gd"],
            tests=["res://tests/test_player.gd"],
            acceptance=["Player can move"],
        )

        tool = CreateGameFromGDDTool()
        result = await tool.execute(project_root=str(temp_project), story_id="001")

        assert "Generated 2 components" in result
        assert "Player" in result
        assert "Enemy" in result
        assert (temp_project / "scripts" / "player.gd").exists()
        assert (temp_project / "scenes" / "player.tscn").exists()
        assert (temp_project / "scenes" / "enemy.tscn").exists()

    async def test_create_game_with_collectible(self, temp_project):
        gdd_tool = GDDCreateTool()
        await gdd_tool.execute(
            project_root=str(temp_project),
            story_id="002",
            title="Coin Game",
            content="Collect coins",
            scenes=["res://scenes/coin.tscn"],
            scripts=["res://scripts/coin.gd"],
            tests=[],
            acceptance=["Coins appear"],
        )

        tool = CreateGameFromGDDTool()
        result = await tool.execute(project_root=str(temp_project), story_id="002")

        assert "Generated 1 components" in result
        assert "Coin" in result
