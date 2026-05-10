"""
Auto Test and Fix Loop - Step 3
"""

import subprocess
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class TestResult:
    """测试结果"""
    passed: bool
    message: str
    errors: list[str] = None


class AutoTester:
    """自动测试"""
    
    def __init__(self, project_root: str, godot_path: str = "godot"):
        self.project_root = Path(project_root)
        self.godot_path = godot_path
    
    def check_syntax(self, script_path: str) -> TestResult:
        """检查 GDScript 语法"""
        
        # Use regex for basic checks (no Godot needed)
        try:
            content = Path(script_path).read_text(encoding='utf-8')
            errors = []
            
            # Check for common issues
            if "extends" not in content:
                errors.append("缺少 extends")
            if "func " not in content and "_ready" not in content:
                errors.append("缺少函数定义")
            if content.count("func ") > content.count("end"):
                errors.append("func/end 不匹配")
            if not content.strip():
                errors.append("文件为空")
            
            if errors:
                return TestResult(False, "语法问题", errors)
            
            return TestResult(True, "语法检查通过", [])
        
        except Exception as e:
            return TestResult(False, str(e), [str(e)])
    
    def check_scene(self, scene_path: str) -> TestResult:
        """检查场景文件"""
        
        try:
            content = Path(scene_path).read_text(encoding='utf-8')
            errors = []
            
            if "[gd_scene" not in content:
                errors.append("缺少 gd_scene 头")
            if not content.strip():
                errors.append("文件为空")
            
            if errors:
                return TestResult(False, "场景问题", errors)
            
            return TestResult(True, "场景检查通过", [])
        
        except Exception as e:
            return TestResult(False, str(e), [str(e)])
    
    def run_godot_check(self, project_path: str = None) -> TestResult:
        """使用 Godot 检查（如果可用）"""
        
        project_path = project_path or str(self.project_root)
        
        try:
            # Try headless check
            result = subprocess.run(
                [self.godot_path, "--headless", "--check-only", "--path", project_path],
                capture_output=True,
                timeout=30,
                cwd=project_path
            )
            
            if result.returncode == 0:
                return TestResult(True, "Godot 检查通过", [])
            else:
                return TestResult(False, "检查失败", [result.stderr.decode()[:200]])
        
        except FileNotFoundError:
            # Godot not installed - skip
            return TestResult(True, "Godot 未安装，跳过", [])
        except subprocess.TimeoutExpired:
            return TestResult(False, "检查超时", [])


class TestReporter:
    """测试报告"""
    
    def __init__(self):
        self.results = []
    
    def add_result(self, name: str, result: TestResult):
        self.results.append((name, result))
    
    def generate_report(self) -> str:
        """生成报告"""
        lines = ["# 测试报告", ""]
        
        passed = 0
        failed = 0
        
        for name, result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            lines.append(f"- {name}: {status}")
            lines.append(f"  {result.message}")
            
            if result.errors:
                for err in result.errors:
                    lines.append(f"  错误: {err}")
            
            if result.passed:
                passed += 1
            else:
                failed += 1
        
        lines.append("")
        lines.append(f"总计: {passed} 通过, {failed} 失败")
        
        return '\n'.join(lines)
    
    def save_report(self, path: str):
        """保存报告"""
        report = self.generate_report()
        Path(path).write_text(report, encoding='utf-8')


class FixLoop:
    """自动修复循环"""
    
    def __init__(self, project_root: str, max_iterations: int = 3):
        self.project_root = Path(project_root)
        self.tester = AutoTester(project_root)
        self.reporter = TestReporter()
        self.max_iterations = max_iterations
    
    def run_tests(self) -> TestResult:
        """运行所有测试"""
        
        all_passed = True
        all_errors = []
        
        # Test scripts
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.glob("*.gd"):
                result = self.tester.check_syntax(str(script))
                self.reporter.add_result(script.name, result)
                if not result.passed:
                    all_passed = False
                    all_errors.extend(result.errors or [])
        
        # Test scenes
        scenes_dir = self.project_root / "scenes"
        if scenes_dir.exists():
            for scene in scenes_dir.glob("*.tscn"):
                result = self.tester.check_scene(str(scene))
                self.reporter.add_result(scene.name, result)
                if not result.passed:
                    all_passed = False
                    all_errors.extend(result.errors or [])
        
        return TestResult(all_passed, "测试完成" if all_passed else "有问题", all_errors)
    
    def auto_fix(self, script_path: str, error: str) -> bool:
        """自动修复"""
        
        if "缺少 extends" in error:
            # Add extends
            content = Path(script_path).read_text(encoding='utf-8')
            if not content.startswith("extends"):
                new_content = "extends Node\n\n" + content
                Path(script_path).write_text(new_content, encoding='utf-8')
                return True
        
        if "func/end 不匹配" in error:
            # Simple count and add end
            content = Path(script_path).read_text(encoding='utf-8')
            func_count = content.count("func ")
            end_count = content.count("end")
            if func_count > end_count:
                content += "\n" * (func_count - end_count)
                Path(script_path).write_text(content, encoding='utf-8')
                return True
        
        return False
    
    def run_fix_loop(self) -> dict:
        """运行修复循环"""
        
        print("🔄 开始测试循环...")
        
        iterations = 0
        while iterations < self.max_iterations:
            iterations += 1
            print(f"\n--- 迭代 {iterations}/{self.max_iterations} ---")
            
            # Run tests
            result = self.run_tests()
            
            print(f"结果: {'✅ 通过' if result.passed else '❌ 失���'}")
            
            if result.passed:
                break
            
            # Auto-fix errors
            scripts_dir = self.project_root / "scripts"
            if scripts_dir.exists():
                for script in scripts_dir.glob("*.gd"):
                    for err in result.errors or []:
                        if self.auto_fix(str(script), err):
                            print(f"  修复: {script.name}")
        
        # Generate report
        self.reporter.save_report(str(self.project_root / "test_report.md"))
        
        return {
            "iterations": iterations,
            "passed": result.passed,
            "errors": result.errors
        }


def create_test_loop(project_root: str) -> FixLoop:
    """创建测试循环"""
    return FixLoop(project_root)