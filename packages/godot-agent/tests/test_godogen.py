"""Tests for godogen module."""

import pytest
from godot_agent.godogen import GodogenIntegrator, ToolSpec


class TestToolSpec:
    """Tests for ToolSpec dataclass."""
    
    def test_create_tool_spec(self):
        """Test creating a tool specification."""
        spec = ToolSpec(name="generate_sprite", description="Generate a sprite")
        assert spec.name == "generate_sprite"
        assert spec.description == "Generate a sprite"
        assert spec.parameters == []
    
    def test_tool_spec_with_params(self):
        """Test tool spec with parameters."""
        spec = ToolSpec(
            name="generate_state",
            description="Generate a state machine",
            parameters=[{"name": "states", "default": None}]
        )
        assert len(spec.parameters) == 1


class TestGodogenIntegrator:
    """Tests for GodogenIntegrator class."""
    
    def test_create_integrator(self, temp_project):
        """Test creating a godogen integrator."""
        integrator = GodogenIntegrator(str(temp_project))
        assert integrator.project_root == temp_project
        assert integrator.tools == []
    
    def test_load_skill_pack_nonexistent(self, temp_project):
        """Test loading from nonexistent path."""
        integrator = GodogenIntegrator(str(temp_project))
        tools = integrator.load_skill_pack("/nonexistent/path")
        assert tools == []
    
    def test_register_as_mcp_tools_empty(self, temp_project):
        """Test registering with no tools."""
        integrator = GodogenIntegrator(str(temp_project))
        mcp_tools = integrator.register_as_mcp_tools()
        assert mcp_tools == []
    
    def test_generate_state_machine(self, temp_project):
        """Test generating state machine code."""
        integrator = GodogenIntegrator(str(temp_project))
        code = integrator.generate_state_machine(
            name="PlayerState",
            states=["IDLE", "RUN", "JUMP"],
            transitions={"IDLE": "RUN", "RUN": "IDLE"}
        )
        
        assert "PlayerState" in code
        assert "enum State" in code
        assert "IDLE" in code
        assert "RUN" in code
        assert "JUMP" in code
    
    def test_generate_component(self, temp_project):
        """Test generating component code."""
        integrator = GodogenIntegrator(str(temp_project))
        code = integrator.generate_component(
            type="player",
            properties={"health": "int", "speed": "float"}
        )
        
        assert "PlayerComponent" in code
        assert "health" in code
        assert "speed" in code
        assert "extends Node" in code
    
    def test_generate_ui_screen(self, temp_project):
        """Test generating UI screen code."""
        integrator = GodogenIntegrator(str(temp_project))
        code = integrator.generate_ui_screen(
            layout={"name": "MainMenu", "elements": [{"type": "Button", "name": "start"}]}
        )
        
        assert "MainMenuScreen" in code
        assert "extends Control" in code
        assert "start" in code
    
    def test_generate_state_machine_single_state(self, temp_project):
        """Test with single state."""
        integrator = GodogenIntegrator(str(temp_project))
        code = integrator.generate_state_machine(
            name="SimpleState",
            states=["IDLE"],
            transitions={}
        )
        
        assert "IDLE" in code
        assert "extends Node" in code
    
    def test_generate_component_empty_props(self, temp_project):
        """Test with empty properties."""
        integrator = GodogenIntegrator(str(temp_project))
        code = integrator.generate_component("test", {})
        
        assert "TestComponent" in code
    
    def test_generate_ui_screen_empty(self, temp_project):
        """Test with empty layout."""
        integrator = GodogenIntegrator(str(temp_project))
        code = integrator.generate_ui_screen({})
        
        assert "Screen" in code