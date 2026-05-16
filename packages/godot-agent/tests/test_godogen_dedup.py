"""Tests for godogen skill loading deduplication."""

import pytest
from godot_agent.godogen import GodogenIntegrator


class TestGodogenDedup:
    def test_load_all_no_duplicates(self):
        integrator = GodogenIntegrator(".")
        first = integrator.load_all()
        second = integrator.load_all()
        # Second load should return 0 new tools
        assert len(second) == 0
        assert len(integrator.tools) == len(first)

    def test_load_skill_pack_no_duplicates(self, temp_project):
        # Create a skill pack directory
        pack_dir = temp_project / "skills" / "pack1"
        pack_dir.mkdir(parents=True)
        (pack_dir / "test_skill.yaml").write_text(
            "name: test_skill\ndescription: A test skill\ntemplate: |\n  extends Node\n",
            encoding="utf-8",
        )

        integrator = GodogenIntegrator(str(temp_project))
        first = integrator.load_skill_pack(str(pack_dir))
        assert len(first) == 1

        second = integrator.load_skill_pack(str(pack_dir))
        assert len(second) == 0
        assert len(integrator.tools) == 1
