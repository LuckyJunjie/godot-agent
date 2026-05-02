"""
Godot Agent - AI Agent for Godot 4.x Game Development
Derived from nano-bot, focused on Godot-specific tooling.
"""

from godot_agent.scene import SceneDocument, ResourceDocument
from godot_agent.lsp import GDScriptLSPClient
from godot_agent.gdd import GDDEngine, GDDStory
from godot_agent.assets import AssetPipeline, ImageMeta, AudioMeta, ModelMeta
from godot_agent.harness import HarnessRunner, TestResult, SceneResult
from godot_agent.godogen import GodogenIntegrator, ToolSpec

__version__ = "0.1.0"
__author__ = "Newton Team"

__all__ = [
    "SceneDocument",
    "ResourceDocument", 
    "GDScriptLSPClient",
    "GDDEngine",
    "GDDStory",
    "AssetPipeline",
    "ImageMeta",
    "AudioMeta",
    "ModelMeta",
    "HarnessRunner",
    "TestResult",
    "SceneResult",
    "GodogenIntegrator",
    "ToolSpec",
]