"""
Real LLM Integration for godot-agent
使用 MiniMax API (如果配置了)
"""

import os
import json
from typing import Optional

class MiniMaxClient:
    """MiniMax API 客户端"""
    
    def __init__(self, config_path: str = None):
        self.api_key = None
        self.base_url = "https://api.minimax.chat/v1"
        self.model = "minimax-portal/MiniMax-M2.5"
        
        # 加载配置
        if config_path:
            self._load_config(config_path)
        else:
            # 尝试默认路径
            default_paths = [
                "./minimax.json",
                "../minimax.json", 
                "~/.openclaw/minimax.json"
            ]
            for p in default_paths:
                if os.path.exists(os.path.expanduser(p)):
                    self._load_config(p)
                    break
    
    def _load_config(self, path: str):
        """加载配置文件"""
        try:
            config = json.load(open(path))
            self.api_key = config.get("api_key")
            self.model = config.get("model", self.model)
            self.base_url = config.get("base_url", self.base_url)
        except Exception as e:
            print(f"Config load error: {e}")
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return bool(self.api_key)
    
    def chat(self, messages: list, **kwargs) -> str:
        """调用 API"""
        if not self.is_available():
            return None
        
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        try:
            resp = requests.post(
                f"{self.base_url}/text/chatcompletion_v2",
                headers=headers,
                json=data,
                timeout=30
            )
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"API error: {e}")
            return None


def get_llm_client() -> MiniMaxClient:
    """获取 LLM 客户端"""
    return MiniMaxClient()
