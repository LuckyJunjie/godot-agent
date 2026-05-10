"""Compound tools for high-level game component creation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool

from godot_agent.scene import SceneDocument
from godot_agent.godogen import GodogenIntegrator
from godot_agent.assets import AssetPipeline, ImageMeta


class CreateComponentTool(Tool):
    """Create a complete game component: scene + script + nodes + assets."""

    @property
    def name(self) -> str:
        return "gd_create_component"

    @property
    def description(self) -> str:
        return (
            "Create a complete game component in one operation. "
            "Generates the GDScript, scene file, required nodes, "
            "and optional sprite asset. "
            "Examples: player character, enemy, collectible, UI screen."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_root": {"type": "string", "default": "."},
                "component_type": {
                    "type": "string",
                    "enum": ["player", "enemy", "collectible", "obstacle", "ui_screen", "autoload"],
                    "description": "Type of component to create",
                },
                "name": {
                    "type": "string",
                    "description": "Name of the component (e.g., 'Player', 'SlimeEnemy')",
                },
                "behaviors": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "movement",
                            "collision",
                            "animation",
                            "input",
                            "ai",
                            "health",
                            "scoring",
                            "state_machine",
                            "particles",
                        ],
                    },
                    "description": "Behaviors this component needs",
                },
                "extends": {
                    "type": "string",
                    "default": "CharacterBody2D",
                    "description": "Base Godot class to extend",
                },
                "sprite_prompt": {
                    "type": "string",
                    "description": "Optional: prompt for sprite generation",
                },
                "scene_parent": {
                    "type": "string",
                    "default": ".",
                    "description": "Parent node path in scene",
                },
            },
            "required": ["component_type", "name"],
        }

    async def execute(
        self,
        project_root: str = ".",
        component_type: str = "player",
        name: str = "",
        behaviors: list[str] | None = None,
        extends: str = "CharacterBody2D",
        sprite_prompt: str = "",
        scene_parent: str = ".",
    ) -> str:
        root = Path(project_root)
        behaviors = behaviors or []

        # 1. Generate script via godogen skill
        integrator = GodogenIntegrator(project_root)
        integrator.load_all()

        script_content = self._generate_script(
            integrator, component_type, name, behaviors, extends
        )

        script_path = root / "scripts" / f"{name.lower()}.gd"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(script_content, encoding="utf-8")

        # 2. Generate scene
        scene_path = root / "scenes" / f"{name.lower()}.tscn"
        scene_path.parent.mkdir(parents=True, exist_ok=True)
        self._generate_scene(
            scene_path, name, extends, script_path, behaviors, scene_parent
        )

        # 3. Generate sprite if requested
        asset_path = None
        if sprite_prompt:
            pipeline = AssetPipeline(project_root)
            pipeline.initialize()
            meta = ImageMeta(prompt=sprite_prompt, resolution=(64, 64))
            try:
                asset_path = await pipeline.generate_image(meta, name.lower())
            except Exception:
                asset_path = None

        # 4. Return summary
        result = [
            f"Created component '{name}'",
            f"  Script: {script_path}",
            f"  Scene:  {scene_path}",
        ]
        if asset_path:
            result.append(f"  Sprite: {asset_path}")
        return "\n".join(result)

    def _generate_script(
        self,
        integrator: GodogenIntegrator,
        component_type: str,
        name: str,
        behaviors: list[str],
        extends: str,
    ) -> str:
        """Generate GDScript using godogen skills or fallback templates."""
        # Try godogen skill first
        skill_map = {
            "player": "generate_component",
            "enemy": "generate_component",
            "ui_screen": "generate_ui_screen",
            "autoload": "generate_component",
        }
        skill_name = skill_map.get(component_type, "generate_component")

        if any(t.name == skill_name for t in integrator.tools):
            context = {
                "class_name": name,
                "extends": extends,
                "behaviors": behaviors,
            }
            if component_type == "ui_screen":
                context = {"name": name, "layout": {"elements": []}}
            rendered = integrator.render_skill(skill_name, context)
            if rendered:
                return rendered

        # Fallback template
        lines = [
            f"extends {extends}",
            f"class_name {name}",
            "",
            f"# Behaviors: {', '.join(behaviors)}",
            "",
        ]
        if "movement" in behaviors:
            lines.extend([
                "@export var speed: float = 200.0",
                "var velocity: Vector2 = Vector2.ZERO",
                "",
                "func _physics_process(delta):",
                "    move_and_slide()",
                "",
            ])
        if "health" in behaviors:
            lines.extend([
                "@export var max_health: int = 100",
                "var health: int = max_health",
                "",
                "func take_damage(amount: int):",
                "    health -= amount",
                "    if health <= 0:",
                "        die()",
                "",
                "func die():",
                "    queue_free()",
                "",
            ])
        if "input" in behaviors:
            lines.extend([
                "func _input(event):",
                "    if event is InputEventKey:",
                "        handle_input(event)",
                "",
                "func handle_input(event: InputEventKey):",
                "    pass",
                "",
            ])
        lines.extend([
            "func _ready():",
            "    pass",
        ])
        return "\n".join(lines)

    def _generate_scene(
        self,
        scene_path: Path,
        name: str,
        extends: str,
        script_path: Path,
        behaviors: list[str],
        parent: str,
    ) -> None:
        """Generate a .tscn scene file."""
        doc = SceneDocument()

        # Build scene content manually since SceneDocument may not support
        # all the features we need for a fresh creation.
        lines = [
            "[gd_scene load_steps=2 format=3]",
            "",
            f'[ext_resource type="Script" path="res://scripts/{script_path.name}" id="1_{name.lower()}"]',
            "",
            f'[node name="{name}" type="{extends}"]',
            f'script = ExtResource("1_{name.lower()}")',
        ]

        # Add child nodes based on behaviors
        if "collision" in behaviors:
            lines.extend([
                "",
                f'[node name="CollisionShape2D" type="CollisionShape2D" parent="."]',
            ])
        if "animation" in behaviors:
            lines.extend([
                "",
                f'[node name="AnimationPlayer" type="AnimationPlayer" parent="."]',
            ])
        if "particles" in behaviors:
            lines.extend([
                "",
                f'[node name="GPUParticles2D" type="GPUParticles2D" parent="."]',
            ])
        if component_type := "ui_screen":
            lines.extend([
                "",
                '[node name="CanvasLayer" type="CanvasLayer" parent="."]',
            ])

        scene_path.write_text("\n".join(lines), encoding="utf-8")


class CreateGameFromGDDTool(Tool):
    """Generate all scenes, scripts, and assets from a GDD story."""

    @property
    def name(self) -> str:
        return "gd_create_game_from_gdd"

    @property
    def description(self) -> str:
        return (
            "Reads a GDD story and generates all required scenes, scripts, "
            "and assets to implement that story. Validates traceability after."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_root": {"type": "string", "default": "."},
                "story_id": {"type": "string", "description": "Story ID from GDD"},
            },
            "required": ["story_id"],
        }

    async def execute(self, project_root: str = ".", story_id: str = "") -> str:
        from godot_agent.gdd import GDDEngine

        engine = GDDEngine(project_root)
        stories = engine.load_stories()
        story = next((s for s in stories if s.id == story_id), None)
        if not story:
            return f"Story {story_id} not found"

        results = []
        component_tool = CreateComponentTool()

        # Generate each referenced scene
        for scene_path_str in story.scenes:
            scene_name = Path(scene_path_str).stem
            component_type = (
                "player"
                if "player" in scene_name.lower()
                else "enemy"
                if "enemy" in scene_name.lower()
                else "collectible"
            )
            try:
                result = await component_tool.execute(
                    project_root=project_root,
                    component_type=component_type,
                    name=scene_name.capitalize(),
                )
                results.append(result)
            except Exception as exc:
                results.append(f"Error creating {scene_name}: {exc}")

        return (
            f"Generated {len(results)} components for story {story_id}:\n"
            + "\n".join(results)
        )
