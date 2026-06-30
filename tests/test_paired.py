import pytest

from signaltest.compare import compare_scores, measure_scores
from signaltest.metrics.base import BOOLEAN, NUMERIC
from signaltest.stats.effect import effect_ci_paired
from signaltest.stats.gate import FAIL, is_underpowered_paired
from signaltest.stats.power import samples_for_paired
from signaltest.stats.significance import paired_significance


def test_paired_significance_detects_consistent_shift():
    base = [0.1, 0.3, 0.5, 0.7, 0.9]
    cand = [b - 0.2 for b in base]
    assert paired_significance(base, cand) < 0.1


def test_paired_significance_all_equal_is_one():
    assert paired_significance([0.5, 0.5], [0.5, 0.5]) == 1.0


@pytest.mark.parametrize("base,cand", [([0.5], [0.5]), ([0.1, 0.2], [0.1, 0.2, 0.3])])
def test_paired_significance_validates(base, cand):
    with pytest.raises(ValueError):
        paired_significance(base, cand)


def test_paired_ci_contains_mean_difference():
    base = [0.1, 0.4, 0.6, 0.9, 0.3]
    cand = [b - 0.1 for b in base]
    low, high = effect_ci_paired(base, cand)
    assert low <= -0.1 <= high


def test_paired_ci_constant_difference_collapses():
    assert effect_ci_paired([1.0, 2.0, 3.0], [0.0, 1.0, 2.0]) == (-1.0, -1.0)


def test_paired_ci_validates_length():
    with pytest.raises(ValueError):
        effect_ci_paired([0.1, 0.2], [0.1])


def test_paired_ci_requires_two_samples():
    with pytest.raises(ValueError):
        effect_ci_paired([0.1], [0.2])


def test_underpowered_paired():
    assert is_underpowered_paired(3) is True
    assert is_underpowered_paired(20) is False


def test_samples_for_paired_floor():
    assert samples_for_paired(0.0, 0.1) == 2
    assert samples_for_paired(0.2, 0.05) > 2


def test_paired_beats_unpaired_on_consistent_drop():
    base = [0.1, 0.3, 0.5, 0.7, 0.9, 0.2, 0.4, 0.6, 0.8, 0.95]
    cand = [b - 0.1 for b in base]
    unpaired = compare_scores(base, cand, kind=NUMERIC, min_effect=0.03)
    paired = compare_scores(base, cand, kind=NUMERIC, min_effect=0.03, paired=True)
    assert unpaired.status != FAIL
    assert paired.status == FAIL


def test_paired_requires_numeric():
    with pytest.raises(ValueError):
        measure_scores([1, 0], [0, 1], kind=BOOLEAN, polarity="higher_better", paired=True)
