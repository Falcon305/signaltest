from signaltest.trajectory.diff import render_diff
from signaltest.trajectory.model import Step


def test_identical_has_no_changes():
    a = [Step("search", {"q": "cats"})]
    out = render_diff(a, a)
    assert "- " not in out
    assert "+ " not in out
    assert "search" in out


def test_changed_step_shows_minus_and_plus():
    a = [Step("answer", {"text": "meow"})]
    b = [Step("answer", {"text": "woof"})]
    out = render_diff(a, b)
    assert "- answer({'text': 'meow'})" in out
    assert "+ answer({'text': 'woof'})" in out


def test_added_step_shows_plus():
    a = [Step("search")]
    b = [Step("search"), Step("answer")]
    assert "+ answer" in render_diff(a, b)


def test_removed_step_shows_minus():
    a = [Step("search"), Step("answer")]
    b = [Step("search")]
    assert "- answer" in render_diff(a, b)


def test_empty_renders_empty():
    assert render_diff([], []) == ""
