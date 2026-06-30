from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS, decide_gate, is_underpowered


def test_significant_regression_fails():
    v = decide_gate(0.001, -0.40, min_effect=0.03, n_valid=10)
    assert v.status == FAIL


def test_significant_but_tiny_effect_passes():
    v = decide_gate(0.001, -0.01, min_effect=0.03, n_valid=10)
    assert v.status == PASS


def test_big_effect_but_not_significant_passes():
    v = decide_gate(0.30, -0.40, min_effect=0.03, n_valid=10)
    assert v.status == PASS


def test_improvement_is_not_a_regression():
    v = decide_gate(0.001, 0.40, min_effect=0.03, n_valid=10)
    assert v.status == PASS


def test_too_few_valid_is_inconclusive():
    v = decide_gate(0.001, -0.40, min_effect=0.03, n_valid=1, min_valid=2)
    assert v.status == INCONCLUSIVE


def test_underpowered_pass_is_inconclusive():
    v = decide_gate(0.30, -0.40, min_effect=0.03, n_valid=4, underpowered=True)
    assert v.status == INCONCLUSIVE


def test_lower_better_regression_fails():
    v = decide_gate(0.001, 0.40, polarity="lower_better", min_effect=0.03, n_valid=10)
    assert v.status == FAIL


def test_tiny_samples_are_underpowered():
    assert is_underpowered(2, 2) is True


def test_enough_samples_are_powered():
    assert is_underpowered(10, 10) is False
