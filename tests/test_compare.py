from signaltest.compare import compare_scores
from signaltest.metrics.base import BOOLEAN, LOWER_BETTER, NUMERIC
from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS


def test_clear_numeric_drop_fails():
    baseline = [0.9] * 12
    candidate = [0.6] * 12
    verdict = compare_scores(baseline, candidate, kind=NUMERIC)
    assert verdict.status == FAIL


def test_matching_distributions_pass():
    baseline = [0.8, 0.82, 0.79, 0.81, 0.8, 0.83, 0.78, 0.8]
    candidate = [0.81, 0.79, 0.8, 0.82, 0.8, 0.81, 0.79, 0.8]
    verdict = compare_scores(baseline, candidate, kind=NUMERIC)
    assert verdict.status == PASS


def test_too_few_samples_inconclusive():
    verdict = compare_scores([1.0], [0.5], kind=NUMERIC)
    assert verdict.status == INCONCLUSIVE


def test_boolean_drop_fails():
    baseline = [True] * 20
    candidate = [False] * 16 + [True] * 4
    verdict = compare_scores(baseline, candidate, kind=BOOLEAN)
    assert verdict.status == FAIL


def test_lower_better_increase_fails():
    baseline = [100.0] * 12
    candidate = [180.0] * 12
    verdict = compare_scores(baseline, candidate, kind=NUMERIC, polarity=LOWER_BETTER)
    assert verdict.status == FAIL
