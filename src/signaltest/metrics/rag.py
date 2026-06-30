from typing import Any, Callable

from signaltest.metrics.base import HIGHER_BETTER, NUMERIC


class Faithfulness:
    """Scores how well an answer is grounded in its retrieved context.

    `judge(answer, context) -> float in [0, 1]` is supplied by you, so no LLM
    provider is baked in. In a `Case`, `expected` is the context.
    """

    kind = NUMERIC
    polarity = HIGHER_BETTER

    def __init__(self, judge: Callable[[Any, Any], float], name: str = "faithfulness") -> None:
        self.judge = judge
        self.name = name

    def score(self, output: Any, expected: Any) -> float:
        return float(self.judge(output, expected))


class AnswerRelevancy:
    """Scores how relevant an answer is to the question.

    `judge(answer, question) -> float in [0, 1]` is supplied by you. In a `Case`,
    `expected` is the question.
    """

    kind = NUMERIC
    polarity = HIGHER_BETTER

    def __init__(self, judge: Callable[[Any, Any], float], name: str = "answer_relevancy") -> None:
        self.judge = judge
        self.name = name

    def score(self, output: Any, expected: Any) -> float:
        return float(self.judge(output, expected))
