"""Configuration loader for Godot Agent."""

import json
import os
from pathlib import Path
from typing import Optional

from godot_agent.config.schema import GodotAgentConfig


DEFAULT_CONFIG_PATHS = [
    Path.home() / ".godot-agent" / "config.json",
    Path.cwd() / "godot-agent.json",
    Path.cwd() / ".godot-agent.json",
]


def load_config(path: Optional[str | Path] = None) -> GodotAgentConfig:
    """Load Godot Agent configuration.
    
    Args:
        path: Explicit config path. If None, searches default locations.
    
    Returns:
        GodotAgentConfig instance.
    """
    if path:
        config_path = Path(path)
    else:
        config_path = _find_config()
    
    if config_path and config_path.exists():
        raw = json.loads(config_path.read_text())
        # Resolve env vars like ${VAR_NAME}
        raw = _resolve_env_vars(raw)
        return GodotAgentConfig.model_validate(raw)
    
    return GodotAgentConfig()


def _find_config() -> Optional[Path]:
    """Find config file in default locations."""
    for p in DEFAULT_CONFIG_PATHS:
        if p.exists():
            return p
    return None


def _resolve_env_vars(obj):
    """Recursively resolve ${VAR} placeholders from environment."""
    if isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_env_vars(v) for v in obj]
    elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
        var_name = obj[2:-1]
        return os.environ.get(var_name, obj)
    return obj


def save_config(config: GodotAgentConfig, path: Optional[str | Path] = None) -> Path:
    """Save configuration to file.
    
    Args:
        config: Config to save.
        path: Target path. Defaults to ~/.godot-agent/config.json.
    
    Returns:
        Path where config was saved.
    """
    target = Path(path) if path else DEFAULT_CONFIG_PATHS[0]
    target.parent.mkdir(parents=True, exist_ok=True)
    
    data = config.model_dump(by_alias=True, exclude_none=True)
    target.write_text(json.dumps(data, indent=2))
    return target
