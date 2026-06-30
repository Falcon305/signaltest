from signaltest.metrics.base import HIGHER_BETTER, NUMERIC
from signaltest.metrics.trajectory import TrajectoryMatch
from signaltest.trajectory.model import Step


def test_identical_trajectory_scores_one():
    traj = [Step("search", {"q": "cats"}), Step("answer", {"text": "meow"})]
    assert TrajectoryMatch().score(traj, traj) == 1.0


def test_diverged_trajectory_scores_below_one():
    expected = [Step("search"), Step("answer")]
    output = [Step("search"), Step("delete")]
    assert TrajectoryMatch().score(output, expected) == 0.5


def test_ignore_keys_are_respected():
    expected = [Step("search", {"q": "cats", "ts": 1})]
    output = [Step("search", {"q": "cats", "ts": 999})]
    assert TrajectoryMatch(ignore_keys=("ts",)).score(output, expected) == 1.0


def test_declares_numeric_higher_better():
    m = TrajectoryMatch()
    assert m.kind == NUMERIC
    assert m.polarity == HIGHER_BETTER
