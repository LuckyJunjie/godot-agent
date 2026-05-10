"""Missing bridge tools for end-to-end game generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool

from godot_agent.inspector import ProjectInspector


class CreateScriptTool(Tool):
    """Create a GDScript file from a template."""

    @property
    def name(self) -> str:
        return "gd_create_script"

    @property
    def description(self) -> str:
        return (
            "Create a GDScript file from a built-in template. "
            "Templates include: node2d, character_body_2d, autoload, state, resource."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to create"},
                "template": {
                    "type": "string",
                    "enum": ["node2d", "character_body_2d", "autoload", "state", "resource"],
                    "description": "Template to use",
                },
                "class_name": {
                    "type": "string",
                    "description": "Class name for the script",
                },
                "extends": {
                    "type": "string",
                    "default": "Node2D",
                    "description": "Base Godot class to extend",
                },
            },
            "required": ["path", "template"],
        }

    async def execute(
        self,
        path: str,
        template: str,
        class_name: str = "",
        extends: str = "Node2D",
    ) -> str:
        fp = Path(path)
        fp.parent.mkdir(parents=True, exist_ok=True)

        name = class_name or fp.stem.capitalize()

        templates = {
            "node2d": [
                f"extends {extends}",
                f"class_name {name}",
                "",
                "func _ready():",
                "    pass",
            ],
            "character_body_2d": [
                "extends CharacterBody2D",
                f"class_name {name}",
                "",
                "@export var speed: float = 200.0",
                "@export var jump_velocity: float = -400.0",
                "",
                "func _physics_process(delta):",
                "    if not is_on_floor():",
                "        velocity += get_gravity() * delta",
                "    move_and_slide()",
            ],
            "autoload": [
                "extends Node",
                f"class_name {name}",
                "",
                "func _ready():",
                '    print("Autoload ready: {name}")',
                "",
                "func _notification(what):",
                "    if what == NOTIFICATION_WM_CLOSE_REQUEST:",
                "        _save_state()",
                "",
                "func _save_state():",
                "    pass",
            ],
            "state": [
                "extends Node",
                f"class_name {name}",
                "",
                "signal state_changed(new_state)",
                "",
                "enum State { IDLE, ACTIVE, FINISHED }",
                "var current_state: State = State.IDLE",
                "",
                "func enter_state(state: State):",
                "    current_state = state",
                "    state_changed.emit(state)",
                "",
                "func update(delta: float):",
                "    pass",
            ],
            "resource": [
                "extends Resource",
                f"class_name {name}",
                "",
                "@export var id: String = \"\"",
                "@export var display_name: String = \"\"",
                "",
                "func to_dict() -> Dictionary:",
                "    return {\"id\": id, \"display_name\": display_name}",
            ],
        }

        content = "\n".join(templates.get(template, templates["node2d"]))
        fp.write_text(content, encoding="utf-8")
        return f"Created script: {path} ({template} template)"


class SetInputActionTool(Tool):
    """Add or modify input actions in project.godot."""

    @property
    def name(self) -> str:
        return "gd_set_input_action"

    @property
    def description(self) -> str:
        return (
            "Add or update an input action in the project's project.godot file. "
            "Creates the [input] section if it doesn't exist."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_root": {"type": "string", "default": "."},
                "action_name": {"type": "string", "description": "Name of the input action"},
                "keys": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of key names (e.g., KEY_W, KEY_SPACE, KEY_UP)",
                },
                "deadzone": {"type": "number", "default": 0.5},
            },
            "required": ["action_name", "keys"],
        }

    async def execute(
        self,
        project_root: str = ".",
        action_name: str = "",
        keys: list[str] | None = None,
        deadzone: float = 0.5,
    ) -> str:
        keys = keys or []
        project_file = Path(project_root) / "project.godot"
        if not project_file.exists():
            return f"Error: {project_file} not found"

        content = project_file.read_text(encoding="utf-8")

        # Build the action entry
        events = []
        for key in keys:
            # Simple keycode lookup for common keys
            keycode = self._key_to_keycode(key)
            events.append(
                f'Object(InputEventKey,"resource_local_to_scene":false,'
                f'"resource_name":"","device":-1,"window_id":0,'
                f'"alt_pressed":false,"shift_pressed":false,'
                f'"ctrl_pressed":false,"meta_pressed":false,'
                f'"pressed":false,"keycode":0,'
                f'"physical_keycode":{keycode},"key_label":0,'
                f'"unicode":0,"echo":false,"script":null)'
            )

        action_line = (
            f'{action_name}={{"deadzone": {deadzone}, '
            f'"events": [{",".join(events)}]}}'
        )

        if "[input]" not in content:
            content += f"\n\n[input]\n\n{action_line}\n"
        else:
            # Insert after the [input] section header
            idx = content.find("[input]") + len("[input]")
            content = content[:idx] + f"\n\n{action_line}\n" + content[idx:]

        project_file.write_text(content, encoding="utf-8")
        return f"Set input action '{action_name}' with keys: {keys}"

    @staticmethod
    def _key_to_keycode(key: str) -> int:
        """Map key name to Godot Key enum value."""
        # Common keys
        mapping = {
            "KEY_W": 87,
            "KEY_A": 65,
            "KEY_S": 83,
            "KEY_D": 68,
            "KEY_UP": 4194320,
            "KEY_DOWN": 4194322,
            "KEY_LEFT": 4194319,
            "KEY_RIGHT": 4194321,
            "KEY_SPACE": 32,
            "KEY_ENTER": 4194309,
            "KEY_ESCAPE": 4194305,
            "KEY_TAB": 4194306,
            "KEY_SHIFT": 4194325,
            "KEY_CTRL": 4194326,
            "KEY_ALT": 4194328,
        }
        return mapping.get(key.upper(), 0)


class ProjectInspectTool(Tool):
    """Bridge tool wrapper for the existing ProjectInspector."""

    @property
    def name(self) -> str:
        return "gd_project_inspect"

    @property
    def description(self) -> str:
        return (
            "Analyze a Godot project structure, stats, and warnings. "
            "Returns scene count, script count, autoloads, input actions, and detected issues."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_root": {"type": "string", "default": "."}
            },
        }

    async def execute(self, project_root: str = ".") -> str:
        inspector = ProjectInspector(project_root)
        report = inspector.inspect()
        lines = [
            f"Project: {report.project_name or '(unnamed)'}",
            f"Scenes: {len(report.scenes)}, Scripts: {len(report.scripts)}",
            f"Autoloads: {len(report.autoloads)}",
            f"Warnings: {len(report.warnings)}",
        ]
        for w in report.warnings:
            lines.append(f"  ⚠️ {w}")
        return "\n".join(lines)


class ExportGameTool(Tool):
    """Export the game to a runnable binary."""

    @property
    def name(self) -> str:
        return "gd_export_game"

    @property
    def description(self) -> str:
        return (
            "Export the Godot project to a runnable binary for a target platform. "
            "Requires Godot export presets to be configured."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_root": {"type": "string", "default": "."},
                "preset": {
                    "type": "string",
                    "default": "Windows Desktop",
                    "description": "Export preset name from project.godot",
                },
                "output_path": {
                    "type": "string",
                    "description": "Output file path",
                },
            },
            "required": ["output_path"],
        }

    async def execute(
        self,
        project_root: str = ".",
        preset: str = "Windows Desktop",
        output_path: str = "",
    ) -> str:
        import subprocess

        try:
            result = subprocess.run(
                [
                    "godot",
                    "--headless",
                    "--export-release",
                    preset,
                    output_path,
                    "--path",
                    project_root,
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                return f"✅ Exported to {output_path}"
            return f"❌ Export failed:\n{result.stderr}"
        except FileNotFoundError:
            return "⚠️ Godot not installed"
        except subprocess.TimeoutExpired:
            return "⚠️ Export timed out"
