import pytest

from signaltest.stats.significance import boolean_significance


def test_clear_proportion_drop_is_significant():
    baseline = [True] * 20
    candidate = [False] * 16 + [True] * 4
    assert boolean_significance(baseline, candidate) < 0.05


def test_same_proportion_is_not_significant():
    baseline = [True] * 16 + [False] * 4
    candidate = [True] * 15 + [False] * 5
    assert boolean_significance(baseline, candidate) >= 0.05


def test_empty_group_raises():
    with pytest.raises(ValueError, match="at least 1"):
        boolean_significance([], [True, False])
