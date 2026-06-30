from signaltest.metrics.base import HIGHER_BETTER, NUMERIC


class LLMJudge:
    kind = NUMERIC
    polarity = HIGHER_BETTER

    def __init__(self, judge, name="llm_judge"):
        self.judge = judge
        self.name = name

    def score(self, output, expected):
        return float(self.judge(output, expected))
