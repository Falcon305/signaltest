from signaltest.baseline.store import BaselineStore
from signaltest.metrics.numeric import Numeric
from signaltest.runner import Case, check_case


def _case(value):
    return Case("c", run=lambda: value, expected=None, metric=Numeric())


def test_update_re_records_baseline(tmp_path):
    store = BaselineStore(tmp_path / "b.json")
    check_case(_case(1.0), store, n=8)  # cold start records 1.0
    verdict = check_case(_case(0.0), store, n=8, update=True)
    assert verdict.status == "pass"
    assert verdict.reason == "updated baseline"


def test_env_var_forces_update(tmp_path, monkeypatch):
    store = BaselineStore(tmp_path / "b.json")
    check_case(_case(1.0), store, n=8)
    monkeypatch.setenv("SIGNALTEST_UPDATE", "1")
    verdict = check_case(_case(0.0), store, n=8)
    assert verdict.reason == "updated baseline"


def test_without_update_compares(tmp_path):
    store = BaselineStore(tmp_path / "b.json")
    check_case(_case(1.0), store, n=8)
    verdict = check_case(_case(1.0), store, n=8)
    assert verdict.reason != "updated baseline"
