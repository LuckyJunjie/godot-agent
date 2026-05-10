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
                config = json.load(open(config_path))
                self.api_key = config.get("api_key") or os.environ.get(config.get("api_key_env", ""))
                self.model = config.get("model", self.model)
            except:
                pass
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def chat(self, messages: list, **kwargs) -> str:
        if not self.is_available():
            return None
        
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"model": self.model, "messages": messages, **kwargs}
        
        try:
            resp = requests.post(f"{self.base_url}/text/chatcompletion_v2", headers=headers, json=data, timeout=30)
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"API error: {e}")
            return None

def get_llm_client() -> MiniMaxClient:
    return MiniMaxClient()
