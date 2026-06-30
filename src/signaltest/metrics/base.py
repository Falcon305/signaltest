from typing import Any, Protocol, Union

NUMERIC = "numeric"
BOOLEAN = "boolean"

HIGHER_BETTER = "higher_better"
LOWER_BETTER = "lower_better"

Score = Union[bool, float]


class Metric(Protocol):
    name: str
    kind: str
    polarity: str

    def score(self, output: Any, expected: Any) -> Score: ...
