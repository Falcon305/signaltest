from signaltest.metrics.base import LOWER_BETTER, NUMERIC
from signaltest.metrics.contains import Contains
from signaltest.metrics.numeric import Numeric


def test_numeric_passes_value_through():
    assert Numeric().score(0.42) == 0.42


def test_numeric_polarity_is_configurable():
    m = Numeric(name="latency", polarity=LOWER_BETTER)
    assert m.polarity == LOWER_BETTER
    assert m.kind == NUMERIC


def test_contains_true_when_substring_present():
    assert Contains().score("the answer is Paris", "Paris") is True


def test_contains_false_when_absent():
    assert Contains().score("the answer is London", "Paris") is False
