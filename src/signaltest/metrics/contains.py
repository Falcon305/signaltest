from signaltest.metrics.base import BOOLEAN, HIGHER_BETTER


class Contains:
    name = "contains"
    kind = BOOLEAN
    polarity = HIGHER_BETTER

    def score(self, output, expected):
        return expected in output
