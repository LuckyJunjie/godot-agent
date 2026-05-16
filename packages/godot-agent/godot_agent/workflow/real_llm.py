"""
Real LLM Integration for godot-agent - MiniMax API
"""

import os
import json
from typing import Optional

class MiniMaxClient:
    def __init__(self, config_path: str = None):
        self.api_key = None
        self.base_url = "https://api.minimax.chat/v1"
        self.model = "minimax-portal/MiniMax-M2.5"
        
        # Load from env or config file
        self.api_key = os.environ.get("MINIMAX_API_KEY")
        
        if not self.api_key and config_path:
            try:
                with open(config_path) as f:
                    config = json.load(f)
                self.api_key = config.get("api_key") or os.environ.get(config.get("api_key_env", ""))
                self.model = config.get("model", self.model)
            except (OSError, json.JSONDecodeError):
                pass
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def chat(self, messages: list, **kwargs) -> str | None:
        if not self.is_available():
            return None

        import aiohttp

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"model": self.model, "messages": messages, **kwargs}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/text/chatcompletion_v2",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    resp.raise_for_status()
                    result = await resp.json()
                    return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"API error: {e}")
            return None

def get_llm_client() -> MiniMaxClient:
    return MiniMaxClient()
