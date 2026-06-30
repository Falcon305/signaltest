from typing import Any, Callable

from signaltest.metrics.base import HIGHER_BETTER, NUMERIC


class LLMJudge:
    kind = NUMERIC
    polarity = HIGHER_BETTER

    def __init__(self, judge: Callable[[Any, Any], float], name: str = "llm_judge") -> None:
        self.judge = judge
        self.name = name

    def score(self, output: Any, expected: Any) -> float:
        return float(self.judge(output, expected))
