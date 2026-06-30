from signaltest.metrics.exact import ExactMatch
from signaltest.runner import Case, run_suite
from signaltest.stats.gate import FAIL, PASS


def good():
    return "Paris"


def bad():
    return "London"


def geo(run):
    return Case("geo", run=run, expected="Paris", metric=ExactMatch())


def math():
    return Case("math", run=lambda: "4", expected="4", metric=ExactMatch())


def test_suite_records_then_passes(tmp_path):
    path = tmp_path / "b.json"
    first = run_suite([geo(good), math()], path, n=10)
    assert all("record" in v.reason for v in first.values())
    second = run_suite([geo(good), math()], path, n=10)
    assert second["geo"].status == PASS
    assert second["math"].status == PASS


def test_suite_catches_one_regression(tmp_path):
    path = tmp_path / "b.json"
    run_suite([geo(good), math()], path, n=10)
    results = run_suite([geo(bad), math()], path, n=10)
    assert results["geo"].status == FAIL
    assert results["math"].status == PASS
