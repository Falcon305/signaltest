from signaltest.stats.correction import bh_adjust


def test_empty_returns_empty():
    assert bh_adjust([]) == []


def test_single_value_unchanged():
    assert bh_adjust([0.03]) == [0.03]


def test_adjusted_never_below_raw():
    raw = [0.01, 0.02, 0.03, 0.04]
    adjusted = bh_adjust(raw)
    assert all(a >= r for a, r in zip(adjusted, raw))


def test_correction_inflates_with_many_tests():
    raw = [0.01, 0.5, 0.6, 0.7]
    adjusted = bh_adjust(raw)
    assert adjusted[0] > raw[0]
