from typing import Any

from signaltest.metrics.base import BOOLEAN, HIGHER_BETTER


class ExactMatch:
    name = "exact_match"
    kind = BOOLEAN
    polarity = HIGHER_BETTER

    def score(self, output: Any, expected: Any) -> bool:
        return output == expected
