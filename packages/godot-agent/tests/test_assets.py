"""Tests for assets module."""

import pytest
from godot_agent.assets import AssetPipeline, ImageMeta, AudioMeta, ModelMeta


class TestImageMeta:
    def test_create_image_meta(self):
        meta = ImageMeta(prompt="A hero sprite")
        assert meta.prompt == "A hero sprite"
        assert meta.model == "dall-e-3"
        assert meta.resolution == (256, 256)

    def test_image_meta_full(self):
        meta = ImageMeta(prompt="A hero", negative_prompt="blurry", model="midjourney", resolution=(512, 512), tags=["hero"], version=2)
        assert meta.negative_prompt == "blurry"
        assert meta.version == 2


class TestAudioMeta:
    def test_create_audio_meta(self):
        meta = AudioMeta(prompt="Jump sound")
        assert meta.prompt == "Jump sound"
        assert meta.model == "elevenlabs"
        assert meta.duration == 5


class TestModelMeta:
    def test_create_model_meta(self):
        meta = ModelMeta(prompt="A crate")
        assert meta.prompt == "A crate"
        assert meta.model == "trellis"


class TestAssetPipeline:
    def test_create_pipeline(self, temp_project):
        pipeline = AssetPipeline(str(temp_project))
        assert pipeline.project_root == temp_project

    def test_initialize(self, temp_project):
        pipeline = AssetPipeline(str(temp_project))
        pipeline.initialize()
        assert (temp_project / "assets").exists()
        assert (temp_project / "assets" / "generated").exists()

    def test_generate_image(self, temp_project):
        import asyncio
        pipeline = AssetPipeline(str(temp_project))
        pipeline.initialize()
        meta = ImageMeta(prompt="A hero")
        path = asyncio.run(pipeline.generate_image(meta, "hero"))
        assert path is not None
        assert path.name == "hero.png"

    def test_generate_audio(self, temp_project):
        import asyncio
        pipeline = AssetPipeline(str(temp_project))
        pipeline.initialize()
        meta = AudioMeta(prompt="Jump")
        path = asyncio.run(pipeline.generate_audio(meta, "jump"))
        assert path is not None

    def test_generate_model(self, temp_project):
        import asyncio
        pipeline = AssetPipeline(str(temp_project))
        pipeline.initialize()
        meta = ModelMeta(prompt="Crate")
        path = asyncio.run(pipeline.generate_model(meta, "crate"))
        assert path is not None

    def test_get_asset_metadata(self, temp_project):
        pipeline = AssetPipeline(str(temp_project))
        pipeline.initialize()
        meta_file = temp_project / "assets" / "meta" / "hero.meta.yaml"
        meta_file.write_text('prompt: "A hero"\nversion: 1\n')
        meta = pipeline.get_asset_metadata("hero")
        assert meta is not None

    def test_list_assets_sprites(self, temp_project):
        pipeline = AssetPipeline(str(temp_project))
        pipeline.initialize()
        (temp_project / "assets" / "generated" / "sprites" / "hero.png").touch()
        sprites = pipeline.list_assets("sprite")
        assert len(sprites) == 1
