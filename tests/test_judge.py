from signaltest.metrics.base import HIGHER_BETTER, NUMERIC
from signaltest.metrics.judge import LLMJudge


def test_judge_returns_callable_score():
    metric = LLMJudge(judge=lambda output, expected: 0.8)
    assert metric.score("anything", "anything") == 0.8


def test_judge_coerces_to_float():
    metric = LLMJudge(judge=lambda output, expected: 1)
    assert isinstance(metric.score("a", "b"), float)


def test_judge_declares_numeric_higher_better():
    metric = LLMJudge(judge=lambda output, expected: 0.5)
    assert metric.kind == NUMERIC
    assert metric.polarity == HIGHER_BETTER


def test_judge_passes_output_and_expected():
    seen = {}

    def judge(output, expected):
        seen["output"] = output
        seen["expected"] = expected
        return 1.0

    LLMJudge(judge=judge).score("got", "want")
    assert seen == {"output": "got", "expected": "want"}
