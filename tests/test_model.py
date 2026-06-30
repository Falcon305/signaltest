from signaltest.baseline.store import BaselineStore
from signaltest.metrics.exact import ExactMatch
from signaltest.runner import Case, assert_no_regression
from signaltest.stats.gate import PASS


def good():
    return "Paris"


def bad():
    return "London"


def geo(run):
    return Case("geo", run=run, expected="Paris", metric=ExactMatch())


def test_baseline_records_model(tmp_path):
    path = tmp_path / "b.json"
    assert_no_regression(geo(good), path, n=10, model="m1")
    assert BaselineStore(path).load()["geo::exact_match"]["model"] == "m1"


def test_model_change_rerecords_instead_of_failing(tmp_path):
    path = tmp_path / "b.json"
    assert_no_regression(geo(good), path, n=10, model="m1")
    verdict = assert_no_regression(geo(bad), path, n=10, model="m2")
    assert verdict.status == PASS
    assert "model" in verdict.reason
    assert BaselineStore(path).load()["geo::exact_match"]["model"] == "m2"
