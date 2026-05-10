"""Persistent state for game generation projects."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class GameProjectState:
    """Tracks the progress of a game generation project."""

    requirement: str
    project_root: str
    genre: str = ""
    current_phase: str = "idle"  # idle | designing | scaffolding | implementing | testing | polishing | complete
    completed_phases: list[str] = field(default_factory=list)
    pending_phases: list[str] = field(default_factory=list)
    known_issues: list[dict] = field(default_factory=list)
    generated_files: list[str] = field(default_factory=list)
    gdd_path: str = ""
    last_error: str = ""
    metadata: dict = field(default_factory=dict)

    @classmethod
    def load(cls, project_root: str) -> Optional["GameProjectState"]:
        """Load state from disk."""
        path = Path(project_root) / ".godot-agent" / "state.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls(**data)
        except (json.JSONDecodeError, TypeError):
            return None

    def save(self) -> None:
        """Save state to disk."""
        path = Path(self.project_root) / ".godot-agent" / "state.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def mark_phase_complete(self, phase: str) -> None:
        if phase in self.pending_phases:
            self.pending_phases.remove(phase)
        if phase not in self.completed_phases:
            self.completed_phases.append(phase)
        self.save()

    def add_issue(self, phase: str, description: str, severity: str = "warning") -> None:
        self.known_issues.append({
            "phase": phase,
            "description": description,
            "severity": severity,
            "resolved": False,
        })
        self.save()

    def resolve_issue(self, description: str) -> None:
        for issue in self.known_issues:
            if issue["description"] == description:
                issue["resolved"] = True
        self.save()

    def add_generated_file(self, file_path: str) -> None:
        if file_path not in self.generated_files:
            self.generated_files.append(file_path)
            self.save()

    def get_status(self) -> str:
        total = len(self.completed_phases) + len(self.pending_phases)
        open_issues = len([i for i in self.known_issues if not i["resolved"]])
        lines = [
            f"Project: {self.project_root}",
            f"Genre: {self.genre or 'unknown'}",
            f"Phase: {self.current_phase}",
            f"Progress: {len(self.completed_phases)} / {total} phases",
            f"Files: {len(self.generated_files)}",
            f"Issues: {open_issues} open",
        ]
        return "\n".join(lines)
