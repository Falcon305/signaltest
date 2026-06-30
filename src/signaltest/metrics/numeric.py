from typing import Any

from signaltest.metrics.base import HIGHER_BETTER, NUMERIC


class Numeric:
    kind = NUMERIC

    def __init__(self, name: str = "numeric", polarity: str = HIGHER_BETTER) -> None:
        self.name = name
        self.polarity = polarity

    def score(self, output: Any, expected: Any = None) -> float:
        return float(output)
