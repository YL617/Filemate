"""LLM 配置：从环境变量 / .env 加载。"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class LLMConfig:
    provider: str = "deepseek"
    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-v4-flash"
    timeout: float = 60.0
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> LLMConfig:
        return cls(
            provider=os.environ.get("LLM_PROVIDER", "deepseek"),
            api_key=os.environ.get("LLM_API_KEY", ""),
            base_url=os.environ.get("LLM_BASE_URL", "https://api.deepseek.com"),
            model=os.environ.get("LLM_MODEL", "deepseek-v4-flash"),
        )
