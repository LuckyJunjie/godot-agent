"""
Self-Harness Runner
Runs GDScript tests and scene integration tests headlessly.
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import json


@dataclass
class TestResult:
    """Result of a test run."""
    passed: bool
    message: str
    duration: float
    details: Optional[dict] = None


@dataclass
class SceneResult:
    """Result of a scene load test."""
    loaded: bool
    scene_path: str
    duration: float
    error: Optional[str] = None


class HarnessRunner:
    """Runs tests using Godot's --headless mode."""
    
    def __init__(self, project_root: str, godot_path: str = "godot"):
        self.project_root = Path(project_root)
        self.godot_path = godot_path
    
    async def run_unit(self, test_script: str, godot_args: Optional[list] = None) -> TestResult:
        """Run a GDScript unit test."""
        godot_args = godot_args or ["--headless", "--quit"]
        
        cmd = [self.godot_path] + godot_args + [
            "--script", test_script
        ]
        
        start = asyncio.get_event_loop().time()
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=60.0
            )
            
            duration = asyncio.get_event_loop().time() - start
            
            passed = proc.returncode == 0
            
            return TestResult(
                passed=passed,
                message=stdout.decode() if stdout else "",
                duration=duration,
                details={"returncode": proc.returncode}
            )
        except asyncio.TimeoutError:
            return TestResult(
                passed=False,
                message="Test timed out",
                duration=60.0
            )
        except FileNotFoundError:
            return TestResult(
                passed=False,
                message=f"Godot not found: {self.godot_path}",
                duration=0.0
            )
    
    async def run_scene(self, scene_path: str, timeout: float = 30.0) -> SceneResult:
        """Load a scene headlessly."""
        cmd = [
            self.godot_path,
            "--headless",
            "--quit",
            "--path", str(self.project_root),
            scene_path
        ]
        
        start = asyncio.get_event_loop().time()
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
            
            duration = asyncio.get_event_loop().time() - start
            
            loaded = proc.returncode == 0
            error = stderr.decode() if stderr else None
            
            return SceneResult(
                loaded=loaded,
                scene_path=scene_path,
                duration=duration,
                error=error
            )
        except asyncio.TimeoutError:
            return SceneResult(
                loaded=False,
                scene_path=scene_path,
                duration=timeout,
                error="Timeout"
            )
        except FileNotFoundError:
            return SceneResult(
                loaded=False,
                scene_path=scene_path,
                duration=0.0,
                error=f"Godot not found: {self.godot_path}"
            )
    
    async def run_gut_suite(self, suite_path: str) -> TestResult:
        """Run GUT test suite."""
        # GUT (Godot Universal Tester) integration
        # Requires GUT plugin installed
        gut_script = self.project_root / "addons" / "gut" / "gut_plugin.gd"
        
        if not gut_script.exists():
            return TestResult(
                passed=False,
                message="GUT plugin not installed",
                duration=0.0
            )
        
        return await self.run_unit(suite_path)
    
    async def benchmark(self, scene_path: str, duration: float = 10.0) -> dict:
        """Run performance benchmark."""
        cmd = [
            self.godot_path,
            "--headless",
            "--path", str(self.project_root),
            "--script", "res://tests/benchmark.gd"
        ]
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=duration + 10.0
            )
            
            # Parse benchmark results
            try:
                return json.loads(stdout.decode())
            except json.JSONDecodeError:
                return {"raw": stdout.decode()}
        except asyncio.TimeoutError:
            return {"error": "Benchmark timed out"}
    
    def check_syntax_errors(self, file_path: str) -> list[dict]:
        """Check for syntax errors without running Godot."""
        cmd = [
            self.godot_path,
            "--headless",
            "--check-only",
            "--path", str(self.project_root),
            file_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                cwd=str(self.project_root)
            )
            
            errors = []
            if result.returncode != 0:
                errors.append({
                    "message": result.stderr.decode(),
                    "severity": 1
                })
            
            return errors
        except subprocess.TimeoutExpired:
            return [{"message": "Check timed out", "severity": 2}]
        except FileNotFoundError:
            return [{"message": f"Godot not found", "severity": 3}]