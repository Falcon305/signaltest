from dataclasses import dataclass, field


@dataclass
class Step:
    tool: str
    args: dict = field(default_factory=dict)
