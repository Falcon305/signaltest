from signaltest.metrics.base import HIGHER_BETTER, NUMERIC
from signaltest.trajectory.match import match_score


class TrajectoryMatch:
    kind = NUMERIC
    polarity = HIGHER_BETTER

    def __init__(self, name="trajectory_match", ignore_keys=()):
        self.name = name
        self.ignore_keys = ignore_keys

    def score(self, output, expected):
        return match_score(expected, output, ignore_keys=self.ignore_keys)
