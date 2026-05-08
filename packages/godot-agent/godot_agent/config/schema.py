"""Pydantic models for Godot Agent configuration."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class GodotConfig(BaseModel):
    """Godot engine configuration."""
    model_config = ConfigDict(populate_by_name=True)
    
    editor_path: str = Field(default="godot", alias="editorPath")
    project_path: str = Field(default=".", alias="projectPath")
    lsp_port: int = Field(default=6005, alias="lspPort")
    lsp_host: str = Field(default="localhost", alias="lspHost")
    lsp_auto_connect: bool = Field(default=True, alias="lspAutoConnect")
    lsp_fallback: bool = Field(default=True, alias="lspFallback")
    headless_args: list[str] = Field(
        default_factory=lambda: ["--headless", "--quit"],
        alias="headlessArgs"
    )
    export_presets: list[str] = Field(
        default_factory=list,
        alias="exportPresets"
    )


class AssetsConfig(BaseModel):
    """Asset generation configuration."""
    model_config = ConfigDict(populate_by_name=True)
    
    image_provider: str = Field(default="dall-e-3", alias="imageProvider")
    image_api_key: Optional[str] = Field(default=None, alias="imageApiKey")
    audio_provider: str = Field(default="elevenlabs", alias="audioProvider")
    audio_api_key: Optional[str] = Field(default=None, alias="audioApiKey")
    model_provider: str = Field(default="trellis", alias="modelProvider")
    model_api_key: Optional[str] = Field(default=None, alias="modelApiKey")
    output_dir: str = Field(default="assets/generated", alias="outputDir")
    meta_dir: str = Field(default="assets/meta", alias="metaDir")
    style_guide: str = Field(default="gdd/assets/style-guide.md", alias="styleGuide")
    default_resolution: list[int] = Field(default=[256, 256], alias="defaultResolution")
    default_audio_duration: float = Field(default=3.0, alias="defaultAudioDuration")
    auto_import: bool = Field(default=True, alias="autoImport")
    auto_reference: bool = Field(default=False, alias="autoReference")


class HarnessConfig(BaseModel):
    """Test harness configuration."""
    model_config = ConfigDict(populate_by_name=True)
    
    auto_run: bool = Field(default=True, alias="autoRun")
    auto_run_delay_sec: int = Field(default=2, alias="autoRunDelaySec")
    test_dir: str = Field(default="res://tests", alias="testDir")
    timeout_sec: int = Field(default=30, alias="timeoutSec")
    gut_addon_path: str = Field(default="res://addons/gut", alias="gutAddonPath")
    coverage_enabled: bool = Field(default=True, alias="coverageEnabled")


class GodotAgentConfig(BaseModel):
    """Top-level Godot Agent configuration."""
    model_config = ConfigDict(populate_by_name=True)
    
    godot: GodotConfig = Field(default_factory=GodotConfig)
    assets: AssetsConfig = Field(default_factory=AssetsConfig)
    harness: HarnessConfig = Field(default_factory=HarnessConfig)
    godogen_skills_dir: str = Field(
        default="skills/godogen",
        alias="godogenSkillsDir"
    )
