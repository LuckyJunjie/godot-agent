"""
Addons module - Godot addon management.
"""

import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class AddonInfo:
    """Information about an addon."""
    name: str
    path: str
    version: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None


class AddonManager:
    """Manages Godot addons."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.addons_dir = self.project_root / "addons"
    
    def list_addons(self) -> list[AddonInfo]:
        """List installed addons."""
        addons = []
        
        if not self.addons_dir.exists():
            return addons
        
        for item in self.addons_dir.iterdir():
            if item.is_dir():
                # Try to get info from plugin.cfg or .plugin
                info = self._parse_addon_info(item)
                addons.append(info)
        
        return addons
    
    def _parse_addon_info(self, addon_path: Path) -> AddonInfo:
        """Parse addon information."""
        name = addon_path.name
        
        # Check for plugin.cfg
        cfg_file = addon_path / "plugin.cfg"
        if cfg_file.exists():
            content = cfg_file.read_text()
            # Simple parsing
            for line in content.split("\n"):
                if line.startswith("plugin="):
                    name = line.split("=")[1].strip().strip('"')
                elif line.startswith("version="):
                    version = line.split("=")[1].strip().strip('"')
                elif line.startswith("author="):
                    author = line.split("=")[1].strip().strip('"')
        
        return AddonInfo(name=name, path=str(addon_path))
    
    def install(self, addon_url: str, name: Optional[str] = None) -> bool:
        """Install an addon from URL (GitHub)."""
        if not self.addons_dir.exists():
            self.addons_dir.mkdir(parents=True)
        
        target_name = name or addon_url.split("/")[-1].replace(".git", "")
        target_path = self.addons_dir / target_name
        
        try:
            # Clone the repository
            result = subprocess.run(
                ["git", "clone", addon_url, str(target_path)],
                capture_output=True,
                timeout=120
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def update(self, addon_name: str) -> bool:
        """Update an addon."""
        addon_path = self.addons_dir / addon_name
        
        if not addon_path.exists():
            return False
        
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=str(addon_path),
                capture_output=True,
                timeout=60
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def uninstall(self, addon_name: str) -> bool:
        """Uninstall an addon."""
        addon_path = self.addons_dir / addon_name
        
        if not addon_path.exists():
            return False
        
        try:
            shutil.rmtree(addon_path)
            return True
        except OSError:
            return False
    
    def enable(self, addon_name: str) -> bool:
        """Enable an addon in project.godot."""
        # This would edit project.godot - placeholder
        return True
    
    def disable(self, addon_name: str) -> bool:
        """Disable an addon in project.godot."""
        # This would edit project.godot - placeholder
        return True


def create_addon_manager(project_root: str) -> AddonManager:
    """Create an addon manager."""
    return AddonManager(project_root)