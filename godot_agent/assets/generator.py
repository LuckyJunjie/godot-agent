"""Asset generators that call LLM APIs."""

import asyncio
import base64
import hashlib
import io
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import httpx


@dataclass
class GenerationResult:
    """Result of an asset generation."""
    success: bool
    path: Optional[Path] = None
    url: Optional[str] = None
    error: Optional[str] = None
    bytes_data: Optional[bytes] = None


class ImageGenerator:
    """Generate images via LLM image APIs."""

    SUPPORTED_PROVIDERS = ("dall-e-3", "dall-e-2", "stability-ai", "openrouter")

    def __init__(self, api_key: Optional[str] = None, provider: str = "dall-e-3"):
        self.api_key = api_key
        self.provider = provider

    async def generate(
        self,
        prompt: str,
        output_path: Path,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        negative_prompt: str = "",
    ) -> GenerationResult:
        """Generate an image and save to disk."""
        if self.provider in ("dall-e-3", "dall-e-2"):
            return await self._generate_openai(prompt, output_path, size, quality, style)
        elif self.provider == "stability-ai":
            return await self._generate_stability(prompt, output_path, size, negative_prompt)
        elif self.provider == "openrouter":
            return await self._generate_openrouter(prompt, output_path, size)
        else:
            return GenerationResult(success=False, error=f"Unsupported provider: {self.provider}")

    async def _generate_openai(
        self, prompt: str, output_path: Path, size: str, quality: str, style: str
    ) -> GenerationResult:
        if not self.api_key:
            return GenerationResult(success=False, error="OpenAI API key not configured")

        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.provider,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "b64_json",
        }
        if self.provider == "dall-e-3":
            payload["quality"] = quality
            payload["style"] = style

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                b64 = data["data"][0]["b64_json"]
                image_bytes = base64.b64decode(b64)
                output_path.write_bytes(image_bytes)
                return GenerationResult(success=True, path=output_path, bytes_data=image_bytes)
        except httpx.HTTPStatusError as e:
            return GenerationResult(success=False, error=f"OpenAI API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            return GenerationResult(success=False, error=f"Generation failed: {e}")

    async def _generate_stability(
        self, prompt: str, output_path: Path, size: str, negative_prompt: str
    ) -> GenerationResult:
        if not self.api_key:
            return GenerationResult(success=False, error="Stability AI API key not configured")

        # Map size to Stability engine
        engine = "stable-image-ultra"
        url = f"https://api.stability.ai/v2beta/stable-image/generate/{engine}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*",
        }
        # Parse width/height from size
        w, h = size.split("x")
        files = {
            "prompt": (None, prompt),
            "output_format": (None, output_path.suffix.lstrip(".")),
            "width": (None, w),
            "height": (None, h),
        }
        if negative_prompt:
            files["negative_prompt"] = (None, negative_prompt)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, files=files)
                resp.raise_for_status()
                output_path.write_bytes(resp.content)
                return GenerationResult(success=True, path=output_path, bytes_data=resp.content)
        except httpx.HTTPStatusError as e:
            return GenerationResult(success=False, error=f"Stability AI error: {e.response.status_code}")
        except Exception as e:
            return GenerationResult(success=False, error=f"Generation failed: {e}")

    async def _generate_openrouter(
        self, prompt: str, output_path: Path, size: str
    ) -> GenerationResult:
        if not self.api_key:
            return GenerationResult(success=False, error="OpenRouter API key not configured")

        url = "https://openrouter.ai/api/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "prompt": prompt,
            "n": 1,
            "size": size,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                image_url = data["data"][0]["url"]
                # Download the image
                img_resp = await client.get(image_url)
                img_resp.raise_for_status()
                output_path.write_bytes(img_resp.content)
                return GenerationResult(success=True, path=output_path, url=image_url, bytes_data=img_resp.content)
        except httpx.HTTPStatusError as e:
            return GenerationResult(success=False, error=f"OpenRouter error: {e.response.status_code}")
        except Exception as e:
            return GenerationResult(success=False, error=f"Generation failed: {e}")
