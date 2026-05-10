"""Tests for GameProjectState persistence."""

import pytest
import json
from pathlib import Path

from godot_agent.state import GameProjectState


class TestGameProjectState:
    def test_save_and_load(self, temp_project):
        state = GameProjectState(
            requirement="Make a snake game",
            project_root=str(temp_project),
            genre="snake",
            current_phase="designing",
            pending_phases=["design", "scaffold", "implement"],
        )
        state.save()

        loaded = GameProjectState.load(str(temp_project))
        assert loaded is not None
        assert loaded.requirement == "Make a snake game"
        assert loaded.genre == "snake"
        assert loaded.current_phase == "designing"

    def test_mark_phase_complete(self, temp_project):
        state = GameProjectState(
            requirement="Test",
            project_root=str(temp_project),
            pending_phases=["a", "b"],
        )
        state.mark_phase_complete("a")
        assert "a" in state.completed_phases
        assert "a" not in state.pending_phases

    def test_add_and_resolve_issue(self, temp_project):
        state = GameProjectState(
            requirement="Test",
            project_root=str(temp_project),
        )
        state.add_issue("design", "Missing acceptance criteria", "error")
        assert len(state.known_issues) == 1
        assert not state.known_issues[0]["resolved"]

        state.resolve_issue("Missing acceptance criteria")
        assert state.known_issues[0]["resolved"]

    def test_get_status(self, temp_project):
        state = GameProjectState(
            requirement="Test",
            project_root=str(temp_project),
            genre="arcade",
            current_phase="implementing",
            completed_phases=["design"],
            pending_phases=["scaffold", "implement", "test"],
            generated_files=["scripts/player.gd"],
        )
        status = state.get_status()
        assert "arcade" in status
        assert "1 / 4 phases" in status
        assert "0 open" in status  # 0 unresolved issues

    def test_load_nonexistent_returns_none(self, temp_project):
        loaded = GameProjectState.load(str(temp_project))
        assert loaded is None
