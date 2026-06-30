import pytest

from signaltest.baseline.record import key, make_record, update_baseline
from signaltest.baseline.store import BaselineStore
from signaltest.metrics.base import HIGHER_BETTER, NUMERIC
from signaltest.runner import Case, assert_no_regression
from signaltest.stats.gate import INCONCLUSIVE, PASS


class ScoreMetric:
    name = "score"
    kind = NUMERIC
    polarity = HIGHER_BETTER

    def score(self, output, expected):
        return output


def case_from(case_id, scores):
    it = iter(scores)
    return Case(case_id, run=lambda: next(it), expected=None, metric=ScoreMetric())


def seed(path, scores):
    update_baseline(BaselineStore(path), key("c1", "score"), make_record(scores))


def test_cold_start_records_and_passes(tmp_path):
    path = tmp_path / "b.json"
    verdict = assert_no_regression(case_from("c1", [0.9] * 10), path, n=10)
    assert "record" in verdict.reason
    assert BaselineStore(path).load()


def test_no_regression_passes(tmp_path):
    path = tmp_path / "b.json"
    seed(path, [0.9] * 10)
    verdict = assert_no_regression(case_from("c1", [0.9] * 10), path, n=10)
    assert verdict.status == PASS


def test_regression_raises(tmp_path):
    path = tmp_path / "b.json"
    seed(path, [0.9] * 10)
    with pytest.raises(AssertionError):
        assert_no_regression(case_from("c1", [0.5] * 10), path, n=10)


def test_improvement_passes(tmp_path):
    path = tmp_path / "b.json"
    seed(path, [0.5] * 10)
    verdict = assert_no_regression(case_from("c1", [0.9] * 10), path, n=10)
    assert verdict.status == PASS


def test_all_errors_is_inconclusive(tmp_path):
    path = tmp_path / "b.json"
    seed(path, [0.9] * 10)

    def boom():
        raise RuntimeError("agent down")

    case = Case("c1", run=boom, expected=None, metric=ScoreMetric())
    assert assert_no_regression(case, path, n=10).status == INCONCLUSIVE
