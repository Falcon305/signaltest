from signaltest.metrics.base import BOOLEAN, NUMERIC
from signaltest.stats.gate import INCONCLUSIVE, decide_gate
from signaltest.stats.power import advise, samples_for_effect, samples_for_proportion


def test_bigger_effect_needs_fewer_samples():
    assert samples_for_effect(1.0, 0.5) < samples_for_effect(1.0, 0.1)


def test_more_variance_needs_more_samples():
    assert samples_for_effect(2.0, 0.5) > samples_for_effect(0.5, 0.5)


def test_degenerate_inputs_floor_at_two():
    assert samples_for_effect(0.0, 0.5) == 2
    assert samples_for_effect(1.0, 0.0) == 2
    assert samples_for_proportion(0.9, 0.0) == 2


def test_proportion_recommendation_is_positive():
    assert samples_for_proportion(0.8, 0.1) >= 2


def test_advise_dispatches_on_kind():
    numeric = advise([1.0, 2.0, 3.0, 4.0], NUMERIC, 0.5)
    boolean = advise([True, True, False, True], BOOLEAN, 0.1)
    assert numeric >= 2
    assert boolean >= 2


def test_advise_handles_short_baseline():
    assert advise([1.0], NUMERIC, 0.5) == 2
    assert advise([], BOOLEAN, 0.1) == 2


def test_gate_includes_sample_hint_when_underpowered():
    verdict = decide_gate(0.5, -0.01, n_valid=3, underpowered=True, recommended_samples=42)
    assert verdict.status == INCONCLUSIVE
    assert "~42" in verdict.reason
