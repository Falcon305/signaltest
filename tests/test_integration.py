from signaltest.baseline.store import BaselineStore
from signaltest.metrics.base import LOWER_BETTER
from signaltest.metrics.contains import Contains
from signaltest.metrics.numeric import Numeric
from signaltest.metrics.trajectory import TrajectoryMatch
from signaltest.runner import Case, check_case
from signaltest.stats.gate import FAIL, PASS
from signaltest.trajectory.model import Step


def from_list(values):
    it = iter(values)
    return lambda: next(it)


def test_latency_increase_is_caught(tmp_path):
    store = BaselineStore(tmp_path / "b.json")
    metric = Numeric(name="latency", polarity=LOWER_BETTER)
    check_case(Case("api", run=from_list([100.0] * 10), expected=None, metric=metric), store)
    slow = Case("api", run=from_list([300.0] * 10), expected=None, metric=metric)
    assert check_case(slow, store).status == FAIL


def test_latency_stable_passes(tmp_path):
    store = BaselineStore(tmp_path / "b.json")
    metric = Numeric(name="latency", polarity=LOWER_BETTER)
    check_case(Case("api", run=from_list([100.0] * 10), expected=None, metric=metric), store)
    same = Case("api", run=from_list([100.0] * 10), expected=None, metric=metric)
    assert check_case(same, store).status == PASS


def test_contains_regression_is_caught(tmp_path):
    store = BaselineStore(tmp_path / "b.json")
    good = Case("c", run=lambda: "the capital is Paris", expected="Paris", metric=Contains())
    check_case(good, store)
    bad = Case("c", run=lambda: "the capital is London", expected="Paris", metric=Contains())
    assert check_case(bad, store).status == FAIL


def test_trajectory_regression_is_caught(tmp_path):
    store = BaselineStore(tmp_path / "b.json")
    expected = [Step("search"), Step("answer")]
    good = Case("t", run=lambda: list(expected), expected=expected, metric=TrajectoryMatch())
    check_case(good, store)
    bad = Case("t", run=lambda: [Step("search"), Step("delete")], expected=expected, metric=TrajectoryMatch())
    assert check_case(bad, store).status == FAIL
