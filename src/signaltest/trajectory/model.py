from dataclasses import dataclass, field
from typing import Any


@dataclass
class Step:
    tool: str
    args: dict[str, Any] = field(default_factory=dict)
