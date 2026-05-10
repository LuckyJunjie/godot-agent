"""Staging area for atomic multi-file game generation operations."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class StagedChange:
    """A single file change in the staging area."""

    target_path: str
    content: str
    operation: str = "write"  # write | delete | mkdir


class StagingArea:
    """Accumulates changes in a temp directory before atomic application."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="godot_agent_staging_"))
        self.changes: list[StagedChange] = []
        self._original_backup: Optional[Path] = None

    def write_file(self, rel_path: str, content: str) -> None:
        """Stage a file write."""
        target = self.temp_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self.changes.append(StagedChange(rel_path, content, "write"))

    def delete_file(self, rel_path: str) -> None:
        """Stage a file deletion."""
        self.changes.append(StagedChange(rel_path, "", "delete"))

    def preview(self) -> str:
        """Return a human-readable preview of all staged changes."""
        lines = ["=== Staged Changes ==="]
        for change in self.changes:
            if change.operation == "write":
                lines.append(f"  WRITE {change.target_path} ({len(change.content)} chars)")
            elif change.operation == "delete":
                lines.append(f"  DELETE {change.target_path}")
        return "\n".join(lines)

    def apply(self) -> None:
        """Atomically apply all staged changes to the project."""
        # Create backup
        self._original_backup = Path(tempfile.mkdtemp(prefix="godot_agent_backup_"))
        for change in self.changes:
            src = self.project_root / change.target_path
            if src.exists():
                dst = self._original_backup / change.target_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.is_file():
                    shutil.copy2(src, dst)
                elif src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)

        # Apply changes
        for change in self.changes:
            target = self.project_root / change.target_path
            if change.operation == "write":
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(change.content, encoding="utf-8")
            elif change.operation == "delete":
                if target.exists():
                    if target.is_file():
                        target.unlink()
                    elif target.is_dir():
                        shutil.rmtree(target)

    def rollback(self) -> None:
        """Restore project from backup."""
        if not self._original_backup:
            return
        for change in self.changes:
            target = self.project_root / change.target_path
            backup = self._original_backup / change.target_path
            if backup.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                if backup.is_file():
                    shutil.copy2(backup, target)
                elif backup.is_dir():
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(backup, target)
            elif target.exists():
                if target.is_file():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(target)

    def cleanup(self) -> None:
        """Remove temp directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if self._original_backup:
            shutil.rmtree(self._original_backup, ignore_errors=True)
