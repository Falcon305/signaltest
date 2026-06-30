from signaltest.trajectory.match import match_score
from signaltest.trajectory.model import Step


def test_identical_trajectories_match_fully():
    a = [Step("search", {"q": "cats"}), Step("answer", {"text": "meow"})]
    assert match_score(a, a) == 1.0


def test_different_tools_score_zero():
    assert match_score([Step("search")], [Step("delete")]) == 0.0


def test_one_of_two_steps_differs():
    a = [Step("search", {"q": "cats"}), Step("answer", {"text": "meow"})]
    b = [Step("search", {"q": "cats"}), Step("answer", {"text": "woof"})]
    assert match_score(a, b) == 0.5


def test_length_mismatch_lowers_score():
    a = [Step("search"), Step("answer")]
    b = [Step("search")]
    assert match_score(a, b) == 0.5


def test_ignored_keys_do_not_break_match():
    a = [Step("search", {"q": "cats", "ts": 1})]
    b = [Step("search", {"q": "cats", "ts": 999})]
    assert match_score(a, b, ignore_keys=("ts",)) == 1.0


def test_empty_trajectories_match():
    assert match_score([], []) == 1.0
