"""
LLM Integration - Requirement understanding with AI
"""

from typing import Optional
import json


class RequirementLLM:
    """使用 LLM 理解需求并生成 GDD"""
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4o"):
        self.provider = provider
        self.model = model
    
    def parse_requirement(self, user_input: str) -> dict:
        """使用 LLM 解析需求"""
        
        prompt = f"""分析以下游戏需求，提取关键信息：

需求: {user_input}

请以 JSON 格式返回：
{{
    "name": "游戏名称",
    "genre": "游戏类型(snake/platform/puzzle/shooter/racing/rpg)",
    "features": ["特性列表"],
    "core_mechanics": ["核心玩法"],
    "visual_style": "视觉风格",
    "platforms": ["目标平台"]
}}

只返回 JSON，不要其他内容。"""
        
        # Mock response for now - in production, call actual LLM
        return self._mock_parse(user_input)
    
    def _mock_parse(self, user_input: str) -> dict:
        """模拟 LLM 解析"""
        user_input = user_input.lower()
        
        # Detect genre
        genre = "snake" if "贪食蛇" in user_input or "snake" in user_input else "generic"
        if "平台" in user_input or "platform" in user_input:
            genre = "platform"
        if "射击" in user_input or "shoot" in user_input:
            genre = "shooter"
        
        # Detect features
        features = []
        if "双人" in user_input:
            features.append("multiplayer")
        if "霓虹" in user_input or "neon" in user_input:
            features.append("neon_effects")
        if "穿越" in user_input or "wrap" in user_input:
            features.append("wall_wrap")
        if "加速" in user_input or "speed" in user_input:
            features.append("speed_boost")
        if "道具" in user_input or "item" in user_input:
            features.append("powerups")
        
        # Generate name
        name = genre + "_game"
        if "贪食蛇" in user_input:
            name = "neon_snake"
        
        return {
            "name": name,
            "genre": genre,
            "features": features,
            "core_mechanics": ["移动控制", "碰撞检测", "得分系统"],
            "visual_style": "neon" if "neon" in user_input else "pixel",
            "platforms": ["mobile", "desktop"]
        }
    
    def generate_gdd_content(self, req: dict) -> str:
        """生成 GDD 内容"""
        
        content = f"""---
title: {req['name']}
genre: {req['genre']}
status: approved
---

# {req['name']}

## Core Mechanics
{chr(10).join('- ' + m for m in req['core_mechanics'])}

## Features
{chr(10).join('- ' + f for f in req['features'])}

## Visual Style
{req['visual_style']}

## Platforms
{chr(10).join('- ' + p for p in req['platforms'])}

## Acceptance Criteria
- 游戏可以运行
- 基础控制正常
- 得分系统正常
"""
        
        return content
    
    def suggest_improvements(self, current: dict, feedback: str) -> list[str]:
        """根据反馈建议改进"""
        
        # Simple rule-based suggestions
        suggestions = []
        
        if "无趣" in feedback or "boring" in feedback:
            suggestions.append("添加道具系统")
            suggestions.append("添加特殊能力")
        
        if "太难" in feedback or "hard" in feedback:
            suggestions.append("添加难度选择")
            suggestions.append("添加生命系统")
        
        if "太简单" in feedback or "easy" in feedback:
            suggestions.append("增加障碍物")
            suggestions.append("增加时间限制")
        
        return suggestions


class AutoFixer:
    """自动修复代码问题"""
    
    def __init__(self):
        self.max_retries = 3
    
    def fix_parse_error(self, script_path: str, error: str) -> str:
        """修复解析错误"""
        
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Common fixes
        fixes = [
            # Fix tab/space indentation
            (code.replace('\t', '    '), "tab → 4 spaces"),
            # Fix missing export
            (code.replace('@export ', '@export var '), "add @export var"),
            # Fix Vector2 typo
            (code.replace('Vector2 .', 'Vector2.'), "fix Vector2"),
        ]
        
        for fixed_code, fix_name in fixes:
            if fixed_code != code:
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
                return fix_name
        
        return "manual_fix_needed"
    
    def fix_runtime_error(self, script_path: str, error: str) -> str:
        """修复运行时错误"""
        
        # Pattern-based fixes
        if "invalid call" in error:
            # Fix function calls
            pass
        if "null reference" in error:
            # Add null checks
            pass
        
        return "needs_manual_review"


class EnhancedWorkflow:
    """增强的工作流 - 带 LLM"""
    
    def __init__(self, project_root: str):
        from godot_agent.workflow import AgentWorkflow
        self.base = AgentWorkflow(project_root)
        self.llm = RequirementLLM()
        self.autofixer = AutoFixer()
    
    def run_with_llm(self, requirement: str, use_llm: bool = True) -> dict:
        """运行带 LLM 的工作流"""
        
        print(f"🎮 godot-agent: {requirement}")
        
        if use_llm:
            # 1. LLM 解析
            print("🧠 使用 AI 理解需求...")
            req_data = self.llm.parse_requirement(requirement)
            print(f"   → 解析: {req_data}")
            
            # 2. 生成 GDD
            print("📝 生成 GDD...")
            gdd_content = self.llm.generate_gdd_content(req_data)
            print(f"   → GDD 已生成")
        else:
            # Original workflow
            req_data = {"name": "game", "genre": "game"}
        
        # 3. Generate code (call base workflow)
        files = self.base.generator.generate(
            type('R', (), req_data)()
        )
        
        # 4. Auto-validate and fix
        print("🔧 验证代码...")
        issues = self._validate_files(files)
        
        if issues:
            print(f"   ⚠️ 发现 {len(issues)} 个问题")
            for issue in issues[:3]:
                print(f"      - {issue}")
        else:
            print("   ✅ 无问题")
        
        return {
            "requirement": requirement,
            "parsed": req_data,
            "files": files,
            "issues": issues
        }
    
    def _validate_files(self, files) -> list[str]:
        """验证生成的文件"""
        issues = []
        
        for name, path in files.scripts.items():
            from pathlib import Path
            if Path(path).exists():
                content = Path(path).read_text()
                if len(content) < 50:
                    issues.append(f"{name}.gd 内容太少")
                if "extends" not in content:
                    issues.append(f"{name}.gd 缺少 extends")
            else:
                issues.append(f"{name}.gd 不存在")
        
        return issues
    
    def run_with_fix_loop(self, requirement: str) -> dict:
        """带修复循环的工作流"""
        
        result = self.run_with_llm(requirement)
        
        for retry in range(self.autofixer.max_retries):
            if not result["issues"]:
                break
            
            print(f"🔄 尝试修复 ({retry + 1}/{self.autofixer.max_retries})")
            
            # Auto-fix
            for name, path in result["files"].scripts.items():
                fix = self.autofixer.fix_parse_error(path, str(result["issues"]))
                print(f"   → {fix}")
            
            # Re-validate
            result = self.run_with_llm(requirement)
            result["retry"] = retry + 1
        
        return result


def create_enhanced_workflow(project_root: str) -> EnhancedWorkflow:
    """创建增强工作流"""
    return EnhancedWorkflow(project_root)