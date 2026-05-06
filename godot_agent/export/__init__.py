"""
Export module - Game export to multiple platforms.
"""

import subprocess
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExportPreset:
    """Export preset configuration."""
    name: str
    platform: str  # Windows, macOS, Linux, Web
    path: str
    options: dict


class GameExporter:
    """Exports Godot games to multiple platforms."""
    
    def __init__(self, project_root: str, godot_path: str = "godot"):
        self.project_root = Path(project_root)
        self.godot_path = godot_path
        self.presets: list[ExportPreset] = []
    
    def load_presets(self) -> list[ExportPreset]:
        """Load export presets from project.godot."""
        project_file = self.project_root / "project.godot"
        
        if not project_file.exists():
            return []
        
        # Parse export presets (simplified)
        content = project_file.read_text()
        presets = []
        
        # Default presets if not found
        if "export_presets" not in content:
            presets = [
                ExportPreset("Windows", "Windows", "export/win", {}),
                ExportPreset("macOS", "macOS", "export/mac", {}),
                ExportPreset("Linux", "Linux", "export/linux", {}),
                ExportPreset("Web", "Web", "export/web", {}),
            ]
        
        self.presets = presets
        return presets
    
    def export(self, preset_name: str, output_dir: Optional[str] = None) -> bool:
        """Export game to a specific preset."""
        # Find preset
        preset = None
        for p in self.presets:
            if p.name == preset_name:
                preset = p
                break
        
        if not preset:
            return False
        
        output = output_dir or preset.path
        
        # Build Godot export command
        cmd = [
            self.godot_path,
            "--headless",
            "--export-release",
            preset.platform,
            output
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                timeout=600
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def export_all(self, output_dir: str) -> dict[str, bool]:
        """Export to all platforms."""
        results = {}
        
        for preset in self.presets:
            output_path = f"{output_dir}/{preset.platform.lower()}"
            results[preset.name] = self.export(preset.name, output_path)
        
        return results


def create_exporter(project_root: str) -> GameExporter:
    """Create a game exporter."""
    return GameExporter(project_root)