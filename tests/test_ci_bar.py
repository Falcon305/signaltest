from signaltest.report import ci_bar
from signaltest.stats.gate import FAIL, PASS, Verdict


def test_no_ci_gives_empty_bar():
    assert ci_bar(Verdict(PASS, None, None, "ok")) == ""


def test_interval_excluding_zero_keeps_centre_marker():
    # entirely negative interval: zero (centre) is not covered
    bar = ci_bar(Verdict(FAIL, 0.01, -0.18, "r", ci_low=-0.30, ci_high=-0.06), width=21)
    assert bar[10] == "│"
    assert "━" in bar


def test_interval_crossing_zero_marks_centre():
    bar = ci_bar(Verdict(PASS, 0.4, -0.01, "ok", ci_low=-0.10, ci_high=0.12), width=21)
    assert bar[10] == "╋"


def test_bar_has_requested_width():
    bar = ci_bar(Verdict(FAIL, 0.01, -0.2, "r", ci_low=-0.3, ci_high=-0.05), width=15)
    assert len(bar) == 15
