from signaltest.compare import compare_scores
from signaltest.metrics.base import NUMERIC
from signaltest.stats.gate import FAIL, PASS
from signaltest.stats.significance import MANNWHITNEY, PERMUTATION, numeric_significance


def test_mannwhitney_detects_clear_shift():
    baseline = [0.9, 0.91, 0.89, 0.9, 0.92, 0.88, 0.9, 0.91, 0.89, 0.9]
    candidate = [0.6, 0.61, 0.59, 0.6, 0.62, 0.58, 0.6, 0.61, 0.59, 0.6]
    p = numeric_significance(baseline, candidate, test=MANNWHITNEY)
    assert p < 0.05


def test_mannwhitney_quiet_on_overlap():
    baseline = [0.8, 0.81, 0.79, 0.8, 0.82, 0.78, 0.8, 0.81]
    candidate = [0.8, 0.79, 0.81, 0.8, 0.78, 0.82, 0.8, 0.79]
    p = numeric_significance(baseline, candidate, test=MANNWHITNEY)
    assert p >= 0.05


def test_default_is_permutation():
    baseline = [0.9] * 8 + [0.8] * 2
    candidate = [0.6] * 8 + [0.7] * 2
    default = numeric_significance(baseline, candidate)
    explicit = numeric_significance(baseline, candidate, test=PERMUTATION)
    assert default == explicit


def test_compare_scores_accepts_test_choice():
    baseline = [0.9, 0.91, 0.89, 0.9, 0.92, 0.88, 0.9, 0.91, 0.89, 0.9, 0.9, 0.91]
    candidate = [0.6, 0.61, 0.59, 0.6, 0.62, 0.58, 0.6, 0.61, 0.59, 0.6, 0.6, 0.61]
    assert compare_scores(baseline, candidate, kind=NUMERIC, test=MANNWHITNEY).status == FAIL
    quiet = [0.9, 0.91, 0.89, 0.9, 0.92, 0.88, 0.9, 0.91, 0.89, 0.9, 0.9, 0.91]
    assert compare_scores(quiet, quiet, kind=NUMERIC, test=MANNWHITNEY).status == PASS
