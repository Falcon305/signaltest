from signaltest.metrics.base import HIGHER_BETTER, NUMERIC


class Numeric:
    kind = NUMERIC

    def __init__(self, name="numeric", polarity=HIGHER_BETTER):
        self.name = name
        self.polarity = polarity

    def score(self, output, expected=None):
        return float(output)
