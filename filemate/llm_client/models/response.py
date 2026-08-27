"""LLM 响应模型。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResponse:
    text: str
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)

    @property
    def parsed(self) -> dict[str, Any]:
        return json.loads(self.text)
