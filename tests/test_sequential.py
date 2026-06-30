import pytest

from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS
from signaltest.stats.sequential import sample_schedule, sequential_gate


def cycle_sampler(values):
    state = {"i": 0}

    def draw():
        v = values[state["i"] % len(values)]
        state["i"] += 1
        return v

    return draw


def test_schedule_spreads_min_to_max():
    assert sample_schedule(5, 20, 4) == [5, 10, 15, 20]


def test_schedule_single_look_is_max():
    assert sample_schedule(5, 20, 1) == [20]


def test_schedule_dedups_when_range_is_tight():
    sizes = sample_schedule(2, 3, 4)
    assert sizes == sorted(set(sizes))
    assert sizes[-1] == 3


@pytest.mark.parametrize(
    "min_n,max_n,looks",
    [(2, 3, 0), (1, 3, 2), (3, 2, 2)],
)
def test_schedule_validates(min_n, max_n, looks):
    with pytest.raises(ValueError):
        sample_schedule(min_n, max_n, looks)


def test_passes_early_when_unchanged():
    baseline = [1.0] * 8
    verdict = sequential_gate(
        baseline,
        cycle_sampler([1.0]),
        kind="numeric",
        sizes=[5, 10, 15, 20],
    )
    assert verdict.status == PASS
    assert verdict.samples == 5
    assert "CI within threshold" in verdict.reason


def test_fails_early_on_clear_regression():
    baseline = [1.0] * 8
    verdict = sequential_gate(
        baseline,
        cycle_sampler([0.0]),
        kind="numeric",
        sizes=[5, 10, 15, 20],
    )
    assert verdict.status == FAIL
    assert verdict.samples == 5


def test_reaches_max_when_noisy_but_centered():
    baseline = [0.0, 1.0] * 4
    verdict = sequential_gate(
        baseline,
        cycle_sampler([0.0, 1.0]),
        kind="numeric",
        sizes=[4, 8],
    )
    assert verdict.status == PASS
    assert verdict.samples == 8
    assert "CI within threshold" not in verdict.reason


def test_skips_errored_samples():
    baseline = [1.0] * 8
    verdict = sequential_gate(
        baseline,
        cycle_sampler([1.0, None]),
        kind="numeric",
        sizes=[6, 12],
    )
    assert verdict.status == PASS


def test_inconclusive_when_all_samples_error():
    baseline = [1.0] * 8
    verdict = sequential_gate(
        baseline,
        cycle_sampler([None]),
        kind="numeric",
        sizes=[4, 6],
    )
    assert verdict.status == INCONCLUSIVE
    assert verdict.samples == 6


def test_lower_better_rope_pass():
    baseline = [1.0] * 8
    verdict = sequential_gate(
        baseline,
        cycle_sampler([1.0]),
        kind="numeric",
        polarity="lower_better",
        sizes=[5, 10],
    )
    assert verdict.status == PASS
    assert verdict.samples == 5
