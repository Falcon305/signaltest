from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Case:
    case_id: str
    run: Callable[[], Any]
    expected: Any
    metric: Any
