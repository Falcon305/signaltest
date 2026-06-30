import pytest

from signaltest.metrics.exact import ExactMatch
from signaltest.runner import Case, assert_no_regression
from signaltest.stats.gate import PASS


def good():
    return "Paris"


def degraded():
    return "London"


def test_good_agent_passes_offline(tmp_path):
    path = tmp_path / "baseline.json"
    case = Case("geo", run=good, expected="Paris", metric=ExactMatch())
    assert "record" in assert_no_regression(case, path, n=10).reason
    assert assert_no_regression(case, path, n=10).status == PASS


def test_degraded_agent_is_caught(tmp_path):
    path = tmp_path / "baseline.json"
    assert_no_regression(Case("geo", run=good, expected="Paris", metric=ExactMatch()), path, n=10)
    bad = Case("geo", run=degraded, expected="Paris", metric=ExactMatch())
    with pytest.raises(AssertionError):
        assert_no_regression(bad, path, n=10)
