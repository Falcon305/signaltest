from signaltest.metrics.base import BOOLEAN, HIGHER_BETTER
from signaltest.metrics.exact import ExactMatch


def test_exact_match_scores_equal_as_true():
    assert ExactMatch().score("hello", "hello") is True


def test_exact_match_scores_unequal_as_false():
    assert ExactMatch().score("hello", "world") is False


def test_exact_match_declares_boolean_higher_better():
    m = ExactMatch()
    assert m.kind == BOOLEAN
    assert m.polarity == HIGHER_BETTER
