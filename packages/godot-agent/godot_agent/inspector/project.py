"""Analyze a Godot project and produce a structured report."""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScriptInfo:
    """Information about a GDScript file."""
    path: str
    class_name: str = ""
    extends: str = ""
    has_ready: bool = False
    has_process: bool = False
    exports: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    line_count: int = 0


@dataclass
class SceneInfo:
    """Information about a scene file."""
    path: str
    root_type: str = ""
    root_name: str = ""
    node_count: int = 0
    script_path: str = ""
    ext_resources: list[str] = field(default_factory=list)


@dataclass
class ProjectReport:
    """Complete analysis report for a Godot project."""
    project_path: str
    project_name: str = ""
    godot_version: str = ""
    scenes: list[SceneInfo] = field(default_factory=list)
    scripts: list[ScriptInfo] = field(default_factory=list)
    autoloads: list[dict] = field(default_factory=list)
    input_actions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


class ProjectInspector:
    """Inspects a Godot project directory and produces a report."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.project_file = self.project_root / "project.godot"

    def inspect(self) -> ProjectReport:
        """Run full project inspection."""
        report = ProjectReport(project_path=str(self.project_root))

        if not self.project_file.exists():
            report.warnings.append("No project.godot found — is this a Godot project?")
            return report

        self._parse_project_settings(report)
        self._inspect_scenes(report)
        self._inspect_scripts(report)
        self._compute_stats(report)

        return report

    def _parse_project_settings(self, report: ProjectReport):
        """Parse project.godot for name, version, autoloads, input."""
        content = self.project_file.read_text()

        # Project name
        match = re.search(r'config/name="([^"]*)"', content)
        if match:
            report.project_name = match.group(1)

        # Godot version features
        match = re.search(r'config/features=PackedStringArray\(([^)]+)\)', content)
        if match:
            features = match.group(1)
            version_match = re.search(r'"(\d+\.\d+)"', features)
            if version_match:
                report.godot_version = version_match.group(1)

        # Autoloads
        in_autoload_section = False
        for line in content.split('\n'):
            if line.strip() == '[autoload]':
                in_autoload_section = True
                continue
            if line.startswith('[') and line.strip() != '[autoload]':
                in_autoload_section = False
                continue
            if in_autoload_section and line.strip() and '=' in line:
                key = line.split('=')[0].strip()
                value = line.split('=')[1].strip().strip('"')
                is_singleton = value.startswith('*')
                path = value.lstrip('*')
                report.autoloads.append({
                    "name": key,
                    "path": path,
                    "singleton": is_singleton,
                })

        # Input map
        in_input_section = False
        for line in content.split('\n'):
            if line.strip() == '[input]':
                in_input_section = True
                continue
            if line.startswith('[') and line.strip() != '[input]':
                in_input_section = False
                continue
            if in_input_section and line.strip() and '=' in line:
                # Only capture top-level action keys, not sub-properties
                stripped = line.strip()
                if not stripped.startswith('"') and not stripped.startswith('}'):
                    action = stripped.split('=')[0].strip()
                    report.input_actions.append(action)

    def _inspect_scenes(self, report: ProjectReport):
        """Find and inspect all .tscn files."""
        for scene_file in self.project_root.rglob("*.tscn"):
            # Skip Godot cache and import directories
            if ".godot" in scene_file.parts or ".import" in scene_file.parts:
                continue
            rel_path = scene_file.relative_to(self.project_root)
            info = SceneInfo(path=str(rel_path))

            content = scene_file.read_text()
            lines = content.split('\n')

            for line in lines:
                stripped = line.strip()
                if stripped.startswith('[node name="'):
                    info.node_count += 1
                    # Check if root node
                    if 'parent="' not in stripped:
                        match = re.search(r'name="([^"]+)"', stripped)
                        if match:
                            info.root_name = match.group(1)
                        match = re.search(r'type="([^"]+)"', stripped)
                        if match:
                            info.root_type = match.group(1)

                if stripped.startswith('[ext_resource'):
                    match = re.search(r'path="([^"]+)"', stripped)
                    if match:
                        info.ext_resources.append(match.group(1))

            report.scenes.append(info)

    def _inspect_scripts(self, report: ProjectReport):
        """Find and inspect all .gd files."""
        for script_file in self.project_root.rglob("*.gd"):
            # Skip Godot cache and import directories
            if ".godot" in script_file.parts or ".import" in script_file.parts:
                continue
            rel_path = script_file.relative_to(self.project_root)
            info = ScriptInfo(path=str(rel_path))

            content = script_file.read_text()
            lines = content.split('\n')
            info.line_count = len(lines)

            for line in lines:
                stripped = line.strip()

                if stripped.startswith('class_name '):
                    info.class_name = stripped.split()[1]

                if 'extends ' in stripped:
                    parts = stripped.split('extends ')
                    if len(parts) > 1:
                        info.extends = parts[1].split()[0].split('(')[0]

                if stripped.startswith('signal '):
                    sig = stripped.replace('signal ', '').split('(')[0]
                    info.signals.append(sig)

                if stripped.startswith('@export'):
                    info.exports.append(stripped)

                if stripped.startswith('func _ready('):
                    info.has_ready = True

                if stripped.startswith('func _process('):
                    info.has_process = True

            report.scripts.append(info)

    def _compute_stats(self, report: ProjectReport):
        """Compute aggregate statistics."""
        report.stats = {
            "scene_count": len(report.scenes),
            "script_count": len(report.scripts),
            "total_lines": sum(s.line_count for s in report.scripts),
            "autoload_count": len(report.autoloads),
            "input_action_count": len(report.input_actions),
            "nodes_total": sum(s.node_count for s in report.scenes),
        }

    def print_report(self, report: ProjectReport):
        """Print a human-readable report."""
        print(f"Project: {report.project_name or 'Unnamed'}")
        print(f"Path: {report.project_path}")
        print(f"Godot Version: {report.godot_version or 'unknown'}")
        print()
        print("Stats:")
        for key, value in report.stats.items():
            print(f"  {key}: {value}")
        print()

        if report.autoloads:
            print("Autoloads:")
            for a in report.autoloads:
                print(f"  {a['name']} -> {a['path']}")
            print()

        if report.scenes:
            print("Scenes:")
            for s in report.scenes:
                print(f"  {s.path} ({s.node_count} nodes, root: {s.root_type})")
            print()

        if report.scripts:
            print("Scripts:")
            for s in report.scripts:
                print(f"  {s.path} ({s.line_count} lines, class: {s.class_name or 'N/A'})")
            print()

        if report.warnings:
            print("Warnings:")
            for w in report.warnings:
                print(f"  ! {w}")
