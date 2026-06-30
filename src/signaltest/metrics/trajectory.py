from collections.abc import Sequence

from signaltest.metrics.base import HIGHER_BETTER, NUMERIC
from signaltest.trajectory.match import match_score
from signaltest.trajectory.model import Step


class TrajectoryMatch:
    kind = NUMERIC
    polarity = HIGHER_BETTER

    def __init__(self, name: str = "trajectory_match", ignore_keys: Sequence[str] = ()) -> None:
        self.name = name
        self.ignore_keys = ignore_keys

    def score(self, output: Sequence[Step], expected: Sequence[Step]) -> float:
        return match_score(expected, output, ignore_keys=self.ignore_keys)
