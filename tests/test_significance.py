import pytest

from signaltest.stats.significance import numeric_significance


def test_clear_regression_is_significant():
    baseline = [0.90, 0.91, 0.89, 0.92, 0.90, 0.91, 0.88, 0.90, 0.92, 0.89]
    candidate = [0.50, 0.52, 0.49, 0.51, 0.50, 0.48, 0.51, 0.50, 0.49, 0.52]
    assert numeric_significance(baseline, candidate) < 0.05


def test_no_change_is_not_significant():
    baseline = [0.80, 0.82, 0.79, 0.81, 0.80, 0.83, 0.78, 0.81, 0.80, 0.82]
    candidate = [0.81, 0.80, 0.82, 0.79, 0.80, 0.81, 0.83, 0.78, 0.80, 0.81]
    assert numeric_significance(baseline, candidate) >= 0.05


def test_same_inputs_give_same_pvalue():
    baseline = [0.80, 0.75, 0.82, 0.78, 0.81, 0.79, 0.83, 0.77]
    candidate = [0.70, 0.72, 0.68, 0.71, 0.69, 0.73, 0.67, 0.70]
    assert numeric_significance(baseline, candidate) == numeric_significance(baseline, candidate)


def test_too_few_samples_raises():
    with pytest.raises(ValueError, match="at least 2"):
        numeric_significance([0.8], [0.5])
