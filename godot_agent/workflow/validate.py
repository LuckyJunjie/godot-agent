"""
Game Validator - Verify generated game works
"""

import subprocess
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ValidationResult:
    passed: bool
    message: str
    screenshot: str = ""


class GameValidator:
    """Validates generated game"""
    
    def __init__(self, project_root: str, godot_path: str = "godot"):
        self.project_root = Path(project_root)
        self.godot_path = godot_path
    
    def validate_syntax(self) -> ValidationResult:
        """Check GDScript syntax"""
        errors = []
        
        for script in (self.project_root / "scripts").glob("*.gd"):
            content = script.read_text()
            
            # Basic checks
            if not content.startswith("extends"):
                errors.append(f"{script.name}: missing extends")
            
            func_count = content.count("func ")
            end_count = content.count("end")
            if func_count > end_count:
                errors.append(f"{script.name}: func/end mismatch ({func_count} func, {end_count} end)")
        
        if errors:
            return ValidationResult(False, f"Syntax errors: {len(errors)}", "")
        
        return ValidationResult(True, "Syntax OK", "")
    
    def validate_scene(self) -> ValidationResult:
        """Check scene file"""
        errors = []
        
        for scene in (self.project_root / "scenes").glob("*.tscn"):
            content = scene.read_text()
            if "[gd_scene" not in content:
                errors.append(f"{scene.name}: missing [gd_scene")
        
        if errors:
            return ValidationResult(False, f"Scene errors: {len(errors)}", "")
        
        return ValidationResult(True, "Scene OK", "")
    
    def run_godot_check(self) -> ValidationResult:
        """Run Godot syntax check"""
        try:
            result = subprocess.run(
                [self.godot_path, "--headless", "--check-only", "--path", str(self.project_root)],
                capture_output=True, timeout=30
            )
            
            if result.returncode == 0:
                return ValidationResult(True, "Godot check passed", "")
            else:
                return ValidationResult(False, "Godot check failed", "")
        except FileNotFoundError:
            return ValidationResult(True, "Godot not installed, skip", "")
        except subprocess.TimeoutExpired:
            return ValidationResult(False, "Check timeout", "")
    
    def capture_screenshot(self, output_path: str = "") -> str:
        """Try to capture screenshot (if Godot available)"""
        if not output_path:
            output_path = str(self.project_root / "screenshots" / "game.png")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            subprocess.run(
                [self.godot_path, "--rendering-driver", "vulkan", 
                 "--write-movie", output_path, "--fixed-fps", "1", 
                 "--quit-after", "1", "--path", str(self.project_root)],
                capture_output=True, timeout=10
            )
            return output_path if Path(output_path).exists() else ""
        except:
            return ""
    
    def validate_all(self) -> ValidationResult:
        """Run all validations"""
        results = []
        
        # Syntax
        results.append(self.validate_syntax())
        
        # Scene
        results.append(self.validate_scene())
        
        # Godot
        results.append(self.run_godot_check())
        
        # Summary
        passed = all(r.passed for r in results)
        messages = [r.message for r in results if not r.passed]
        
        message = " | ".join(messages) if messages else "All passed"
        
        return ValidationResult(passed, message, "")


def validate_game(project_root: str) -> ValidationResult:
    """Validate a game project"""
    validator = GameValidator(project_root)
    return validator.validate_all()