"""
Agent Workflow - 端到端游戏开发自动化
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from godot_agent.gdd import GDDEngine, GDDStory
from godot_agent.godogen import GodogenIntegrator
from godot_agent.harness import HarnessRunner


@dataclass
class GameRequirement:
    """游戏需求"""
    name: str
    genre: str  # snake, platform, puzzle, etc.
    description: str
    features: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=lambda: ["mobile", "desktop"])


@dataclass
class GameFiles:
    """生成的游戏文件"""
    scenes: dict[str, str] = field(default_factory=dict)
    scripts: dict[str, str] = field(default_factory=dict)
    gdd: str = ""


class RequirementParser:
    """解析需求 → GDD"""
    
    GENRES = ["snake", "platform", "puzzle", "shooter", "racing", "rpg"]
    
    def parse(self, user_input: str) -> GameRequirement:
        """解析用户输入"""
        user_input = user_input.lower()
        
        # 检测游戏类型
        genre = "snake"
        for g in self.GENRES:
            if g in user_input:
                genre = g
                break
        
        # 提取名称
        name_match = re.search(r'["“]([^"”]+)["”]|开发.*?[的]([\w]+)', user_input)
        name = name_match.group(1) if name_match else f"{genre}_game"
        
        # 提取特性
        features = []
        if "双人" in user_input or "multi" in user_input:
            features.append("multiplayer")
        if "霓虹" in user_input or "neon" in user_input:
            features.append("neon_effects")
        if "穿越" in user_input or "wrap" in user_input:
            features.append("wall_wrap")
        
        return GameRequirement(
            name=name,
            genre=genre,
            description=user_input,
            features=features
        )
    
    def to_gdd(self, req: GameRequirement, output_dir: str) -> str:
        """转换为 GDD"""
        gdd = GDDEngine(output_dir)
        gdd.initialize()
        
        # 创建故事
        story = gdd.create_story(
            story_id="001",
            title=req.name,
            content=req.description
        )
        
        # 添加 acceptance
        story.scenes = [f"res://scenes/{req.genre}.tscn"]
        story.scripts = [f"res://scripts/{req.genre}.gd"]
        story.tests = [f"res://tests/test_{req.genre}.gd"]
        
        if "multiplayer" in req.features:
            story.acceptance.append("支持双人模式")
        if "neon_effects" in req.features:
            story.acceptance.append("霓虹发光效果")
        if "wall_wrap" in req.features:
            story.acceptance.append("穿越墙壁")
        
        story.acceptance.extend([
            f"{req.genre} 可以移动",
            "吃到食物变长",
            "碰撞检测正常"
        ])
        
        # 更新
        gdd.update_story("001", 
            scenes=story.scenes,
            scripts=story.scripts,
            tests=story.tests,
            acceptance=story.acceptance,
            status="approved"
        )
        
        return str(Path(output_dir) / "gdd" / "index.md")


class CodeGenerator:
    """代码生成器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.integrator = GodogenIntegrator(project_root)
        self.scripts_dir = Path(project_root) / "scripts"
        self.scenes_dir = Path(project_root) / "scenes"
    
    def generate(self, req: GameRequirement) -> GameFiles:
        """生成游戏代码"""
        files = GameFiles()
        
        # 生成主脚本
        script_content = self._generate_script(req)
        script_path = self.scripts_dir / f"{req.genre}.gd"
        script_path.write_text(script_content, encoding="utf-8")
        files.scripts[req.genre] = str(script_path)
        
        # 生成场景
        scene_content = self._generate_scene(req)
        scene_path = self.scenes_dir / f"{req.genre}.tscn"
        scene_path.write_text(scene_content, encoding="utf-8")
        files.scenes[req.genre] = str(scene_path)
        
        return files
    
    def _generate_script(self, req: GameRequirement) -> str:
        """根据游戏类型生成脚本"""
        
        if req.genre == "snake":
            return self._snake_script(req)
        elif req.genre == "platform":
            return self._platform_script(req)
        else:
            return self._generic_script(req)
    
    def _snake_script(self, req: GameRequirement) -> str:
        """贪食蛇脚本"""
        lines = [
            "#encoding: utf-8",
            "extends Node2D",
            f"class_name {req.name.capitalize()}",
            "",
            "var speed: float = 200.0",
            "var direction: Vector2 = Vector2.RIGHT",
            "var body_parts: Array = []",
            "var score: int = 0",
            "var is_game_over: bool = false",
            "",
            "func _ready():",
            "    pass",
            "",
            "func _process(delta):",
            "    if is_game_over:",
            "        return",
            "    move_snake(delta)",
            "",
            "func move_snake(delta):",
            "    pass",
            "",
            "func _input(event):",
            "    if event is InputEventKey and event.pressed:",
            "        match event.keycode:",
            "            KEY_UP:",
            "                direction = Vector2.UP",
            "            KEY_DOWN:",
            "                direction = Vector2.DOWN",
            "            KEY_LEFT:",
            "                direction = Vector2.LEFT",
            "            KEY_RIGHT:",
            "                direction = Vector2.RIGHT",
        ]
        
        # 添加特性
        if "wall_wrap" in req.features:
            lines.insert(-4, "    var wrap_charges: int = 3")
        
        if "neon_effects" in req.features:
            lines.insert(2, "var glow_enabled: bool = true")
        
        return '\n'.join(lines)
    
    def _platform_script(self, req: GameRequirement) -> str:
        return "extends CharacterBody2D\nclass_name " + req.name.capitalize()
    
    def _generic_script(self, req: GameRequirement) -> str:
        return f"extends Node2D\nclass_name {req.name.capitalize()}\n\nfunc _ready():\n    pass"
    
    def _generate_scene(self, req: GameRequirement) -> str:
        scene = [
            f"[gd_scene load_steps=2 format=3]",
            "",
            f"[ext_resource path=\"res://scripts/{req.genre}.gd\" type=\"Script\" id=1]",
            "",
            "[node name=\"Main\" type=\"Node2D\"]",
        ]
        
        if req.genre == "snake":
            scene.extend([
                "",
                "[node name=\"Snake\" type=\"Node2D\" parent=\".\"]",
                "[node name=\"Camera\" type=\"Camera2D\" parent=\".\"]",
            ])
        
        return '\n'.join(scene)


class AgentWorkflow:
    """端到端工作流"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.parser = RequirementParser()
        self.generator = CodeGenerator(project_root)
        self.harness = HarnessRunner(project_root)
    
    def run(self, requirement: str) -> GameFiles:
        """运行完整工作流"""
        print(f"🤖 godot-agent: 收到需求 - {requirement}")
        
        # 1. 解析需求
        print("📋 解析需求...")
        req = self.parser.parse(requirement)
        print(f"   → 游戏类型: {req.genre}")
        print(f"   → 特性: {req.features}")
        
        # 2. 生成 GDD
        print("📝 生成 GDD...")
        gdd_path = self.parser.to_gdd(req, str(self.project_root))
        print(f"   → GDD: {gdd_path}")
        
        # 3. 生成代码
        print("⚙️ 生成代码...")
        files = self.generator.generate(req)
        print(f"   → 脚本: {list(files.scripts.keys())}")
        print(f"   → 场景: {list(files.scenes.keys())}")
        
        # 4. 验证
        print("✅ 验证代码...")
        self._validate(files)
        
        print("🎉 完成!")
        
        return files
    
    def _validate(self, files: GameFiles):
        """验证生成的文件"""
        for name, path in files.scripts.items():
            if Path(path).exists():
                print(f"   ✓ {name}.gd 存在")
            else:
                print(f"   ✗ {name}.gd 缺失")
        
        for name, path in files.scenes.items():
            if Path(path).exists():
                print(f"   ✓ {name}.tscn 存在")
            else:
                print(f"   ✗ {name}.tscn 缺失")


def create_workflow(project_root: str) -> AgentWorkflow:
    """创建工作流"""
    return AgentWorkflow(project_root)