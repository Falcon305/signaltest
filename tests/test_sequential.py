import pytest

from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS
from signaltest.stats.sequential import alpha_schedule, sample_schedule, sequential_gate


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
    assert verdict.samples is not None and verdict.samples < 20


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


def test_alpha_schedule_pocock_is_flat():
    assert alpha_schedule(0.05, 4, "pocock") == pytest.approx([0.0125] * 4)


def test_alpha_schedule_sums_to_alpha():
    for spending in ("pocock", "obrien_fleming"):
        assert sum(alpha_schedule(0.05, 5, spending)) == pytest.approx(0.05)


def test_alpha_schedule_obrien_fleming_backloads():
    schedule = alpha_schedule(0.05, 4, "obrien_fleming")
    assert schedule[0] < schedule[-1]
    assert schedule == sorted(schedule)
    assert schedule[-1] > 0.0125  # more than the flat share at the final look


def test_alpha_schedule_single_look_is_full_alpha():
    assert alpha_schedule(0.05, 1) == pytest.approx([0.05])


@pytest.mark.parametrize("looks,spending", [(0, "pocock"), (3, "nonsense")])
def test_alpha_schedule_validates(looks, spending):
    with pytest.raises(ValueError):
        alpha_schedule(0.05, looks, spending)


def test_pocock_fails_earlier_than_obrien_fleming():
    base = [1.0] * 8
    pocock = sequential_gate(
        base, cycle_sampler([0.0]), kind="numeric", sizes=[5, 10, 15, 20], spending="pocock"
    )
    obf = sequential_gate(
        base, cycle_sampler([0.0]), kind="numeric", sizes=[5, 10, 15, 20], spending="obrien_fleming"
    )
    assert pocock.status == obf.status == FAIL
    assert pocock.samples is not None and obf.samples is not None
    assert pocock.samples < obf.samples


def test_comparisons_raise_the_fail_bar():
    base = [1.0] * 8
    values = [0.4] * 5 + [1.0] * 3  # permutation p ~ 0.025
    fail = sequential_gate(base, cycle_sampler(values), kind="numeric", sizes=[8])
    held = sequential_gate(base, cycle_sampler(values), kind="numeric", sizes=[8], comparisons=3)
    assert fail.status == FAIL
    assert held.status != FAIL


def test_comparisons_do_not_block_a_clear_regression():
    base = [1.0] * 8
    verdict = sequential_gate(
        base, cycle_sampler([0.0]), kind="numeric", sizes=[5, 10, 15, 20], comparisons=50
    )
    assert verdict.status == FAIL


def test_comparisons_do_not_affect_rope_pass():
    base = [1.0] * 8
    one = sequential_gate(base, cycle_sampler([1.0]), kind="numeric", sizes=[5, 10])
    many = sequential_gate(
        base, cycle_sampler([1.0]), kind="numeric", sizes=[5, 10], comparisons=99
    )
    assert one.status == many.status == PASS
    assert one.samples == many.samples == 5


def test_workers_match_single_threaded():
    base = [1.0] * 8
    serial = sequential_gate(base, cycle_sampler([1.0]), kind="numeric", sizes=[5, 10])
    parallel = sequential_gate(base, lambda: 1.0, kind="numeric", sizes=[5, 10], workers=4)
    assert serial.status == parallel.status == PASS
    assert serial.samples == parallel.samples == 5


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
