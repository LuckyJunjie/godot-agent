"""Root pytest configuration — adds workspace paths for local development."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "nanobot"))
sys.path.insert(0, str(ROOT / "packages" / "godot-agent"))
