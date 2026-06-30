import itertools

from signaltest.baseline.record import key, make_record, update_baseline
from signaltest.baseline.store import BaselineStore
from signaltest.metrics.base import HIGHER_BETTER, NUMERIC
from signaltest.runner import Case, check_case
from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS


class ScoreMetric:
    name = "score"
    kind = NUMERIC
    polarity = HIGHER_BETTER

    def score(self, output, expected):
        return output


def cycling_case(case_id, values):
    pool = itertools.cycle(values)
    return Case(case_id, run=lambda: next(pool), expected=None, metric=ScoreMetric())


def seed(path, scores):
    update_baseline(BaselineStore(path), key("c1", "score"), make_record(scores))


def test_sequential_passes_early_and_reports_samples(tmp_path):
    path = tmp_path / "b.json"
    seed(path, [1.0] * 10)
    verdict = check_case(
        cycling_case("c1", [1.0]), BaselineStore(path), n=4, max_n=20, sequential=True
    )
    assert verdict.status == PASS
    assert verdict.samples == 4


def test_sequential_fails_on_regression(tmp_path):
    path = tmp_path / "b.json"
    seed(path, [1.0] * 10)
    verdict = check_case(
        cycling_case("c1", [0.0]), BaselineStore(path), n=4, max_n=20, sequential=True
    )
    assert verdict.status == FAIL
    assert verdict.samples is not None


def test_sequential_inconclusive_when_baseline_too_small(tmp_path):
    path = tmp_path / "b.json"
    seed(path, [1.0])
    verdict = check_case(cycling_case("c1", [1.0]), BaselineStore(path), n=4, sequential=True)
    assert verdict.status == INCONCLUSIVE


def test_sequential_default_cap_is_three_times_n(tmp_path):
    path = tmp_path / "b.json"
    seed(path, [0.0, 1.0] * 5)
    verdict = check_case(cycling_case("c1", [0.0, 1.0]), BaselineStore(path), n=4, sequential=True)
    assert verdict.samples == 12
