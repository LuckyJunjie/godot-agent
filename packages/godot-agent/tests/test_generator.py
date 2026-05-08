"""Tests for godot_agent.assets.generator."""

import pytest
from pathlib import Path

from godot_agent.assets.generator import ImageGenerator, GenerationResult


class TestImageGenerator:
    def test_init_defaults(self):
        gen = ImageGenerator()
        assert gen.provider == "dall-e-3"
        assert gen.api_key is None

    def test_init_custom(self):
        gen = ImageGenerator(api_key="sk-test", provider="stability-ai")
        assert gen.api_key == "sk-test"
        assert gen.provider == "stability-ai"

    def test_supported_providers(self):
        assert "dall-e-3" in ImageGenerator.SUPPORTED_PROVIDERS
        assert "stability-ai" in ImageGenerator.SUPPORTED_PROVIDERS
        assert "openrouter" in ImageGenerator.SUPPORTED_PROVIDERS

    @pytest.mark.asyncio
    async def test_generate_unsupported_provider(self, tmp_path):
        gen = ImageGenerator(provider="unsupported")
        result = await gen.generate("test", tmp_path / "out.png")
        assert result.success is False
        assert "Unsupported provider" in result.error

    @pytest.mark.asyncio
    async def test_generate_openai_no_key(self, tmp_path):
        gen = ImageGenerator(api_key=None, provider="dall-e-3")
        result = await gen.generate("a cat", tmp_path / "cat.png")
        assert result.success is False
        assert "API key not configured" in result.error

    @pytest.mark.asyncio
    async def test_generate_stability_no_key(self, tmp_path):
        gen = ImageGenerator(api_key=None, provider="stability-ai")
        result = await gen.generate("a cat", tmp_path / "cat.png")
        assert result.success is False
        assert "API key not configured" in result.error

    @pytest.mark.asyncio
    async def test_generate_openrouter_no_key(self, tmp_path):
        gen = ImageGenerator(api_key=None, provider="openrouter")
        result = await gen.generate("a cat", tmp_path / "cat.png")
        assert result.success is False
        assert "API key not configured" in result.error


class TestGenerationResult:
    def test_result_fields(self):
        r = GenerationResult(success=True, path=Path("/tmp/test.png"))
        assert r.success is True
        assert r.path == Path("/tmp/test.png")
        assert r.error is None
