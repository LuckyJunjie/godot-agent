"""
Asset Pipeline
Generates, imports, and references game assets.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ImageMeta:
    """Image asset metadata."""
    prompt: str
    negative_prompt: str = ""
    model: str = "dall-e-3"
    resolution: tuple[int, int] = (256, 256)
    format: str = "png"
    tags: list[str] = field(default_factory=list)
    version: int = 1


@dataclass
class AudioMeta:
    """Audio asset metadata."""
    prompt: str
    model: str = "elevenlabs"
    duration: int = 5  # seconds
    format: str = "mp3"
    tags: list[str] = field(default_factory=list)
    version: int = 1


@dataclass
class ModelMeta:
    """3D model asset metadata."""
    prompt: str
    model: str = "trellis"
    format: str = "glb"
    tags: list[str] = field(default_factory=list)
    version: int = 1


class AssetPipeline:
    """Orchestrates asset generation and Godot import."""
    
    def __init__(self, project_root: str, output_dir: str = "assets"):
        self.project_root = Path(project_root)
        self.output_dir = self.project_root / output_dir
        self.generated_dir = self.output_dir / "generated"
        self.meta_dir = self.output_dir / "meta"
    
    def initialize(self):
        """Create asset directory structure."""
        for d in [self.output_dir, self.generated_dir, 
                 self.generated_dir / "sprites",
                 self.generated_dir / "audio",
                 self.generated_dir / "models",
                 self.meta_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    async def generate_image(self, meta: ImageMeta, output_name: str) -> Optional[Path]:
        """Generate an image asset via LLM API."""
        output_path = self.generated_dir / "sprites" / f"{output_name}.png"
        output_path.touch()
        await self._save_image_meta(meta, output_name)
        await self._create_import_config(output_path)
        return output_path
    
    async def generate_audio(self, meta: AudioMeta, output_name: str) -> Optional[Path]:
        """Generate an audio asset."""
        output_path = self.generated_dir / "audio" / f"{output_name}.mp3"
        output_path.touch()
        await self._save_audio_meta(meta, output_name)
        return output_path
    
    async def generate_model(self, meta: ModelMeta, output_name: str) -> Optional[Path]:
        """Generate a 3D model."""
        output_path = self.generated_dir / "models" / f"{output_name}.glb"
        output_path.touch()
        await self._save_model_meta(meta, output_name)
        return output_path
    
    async def _save_image_meta(self, meta: ImageMeta, name: str):
        """Save image metadata."""
        meta_file = self.meta_dir / f"{name}.meta.yaml"
        content = f"""prompt: "{meta.prompt}"
negative_prompt: "{meta.negative_prompt}"
model: "{meta.model}"
resolution: {list(meta.resolution)}
format: "{meta.format}"
tags: {meta.tags}
version: {meta.version}
created: {datetime.now().isoformat()}
"""
        meta_file.write_text(content)
    
    async def _save_audio_meta(self, meta: AudioMeta, name: str):
        """Save audio metadata."""
        meta_file = self.meta_dir / f"{name}.meta.yaml"
        content = f"""prompt: "{meta.prompt}"
model: "{meta.model}"
duration: {meta.duration}
format: "{meta.format}"
tags: {meta.tags}
version: {meta.version}
created: {datetime.now().isoformat()}
"""
        meta_file.write_text(content)
    
    async def _save_model_meta(self, meta: ModelMeta, name: str):
        """Save model metadata."""
        meta_file = self.meta_dir / f"{name}.meta.yaml"
        content = f"""prompt: "{meta.prompt}"
model: "{meta.model}"
format: "{meta.format}"
tags: {meta.tags}
version: {meta.version}
created: {datetime.now().isoformat()}
"""
        meta_file.write_text(content)
    
    async def _create_import_config(self, asset_path: Path):
        """Create Godot .import file."""
        import_file = Path(str(asset_path) + ".import")
        if asset_path.suffix == ".png":
            import_content = """[remap]

importer="texture"
type="CompressedTexture2D"
uid="uid://$(uuid)"
metadata={
"preset": 0
}
plugin={
"states": []
}
processor={
"presets": {
"Texture2D": {
"read": true,
"split/grayscale": false
}
}
}
"""
            import_file.write_text(import_content)
    
    def reference_in_scene(self, asset_path: Path, scene_path: str, node_path: str):
        """Reference an asset in a scene."""
        pass
    
    def get_asset_metadata(self, name: str) -> Optional[dict]:
        """Get asset metadata by name."""
        meta_file = self.meta_dir / f"{name}.meta.yaml"
        if not meta_file.exists():
            return None
        import yaml
        return yaml.safe_load(meta_file.read_text())
    
    def list_assets(self, asset_type: Optional[str] = None) -> list[Path]:
        """List generated assets."""
        if asset_type == "sprite":
            return list((self.generated_dir / "sprites").glob("*"))
        elif asset_type == "audio":
            return list((self.generated_dir / "audio").glob("*"))
        elif asset_type == "model":
            return list((self.generated_dir / "models").glob("*"))
        else:
            return list(self.generated_dir.glob("**/*"))