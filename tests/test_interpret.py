import pytest

from signaltest.compare import top_regressions
from signaltest.report import describe, format_report, to_markdown
from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS, Verdict


def test_top_regressions_worst_first():
    base = [1.0, 1.0, 1.0, 1.0]
    cand = [0.9, 0.5, 1.0, 0.8]
    result = top_regressions(base, cand)
    assert [i for i, _ in result] == [1, 3, 0]
    assert [d for _, d in result] == pytest.approx([-0.5, -0.2, -0.1])


def test_top_regressions_respects_k():
    base = [1.0, 1.0, 1.0]
    cand = [0.5, 0.6, 0.7]
    assert len(top_regressions(base, cand, k=2)) == 2


def test_top_regressions_excludes_improvements():
    base = [1.0, 1.0]
    cand = [1.2, 0.8]
    assert top_regressions(base, cand) == [(1, pytest.approx(-0.2))]


def test_top_regressions_lower_better():
    base = [1.0, 1.0]
    cand = [1.5, 0.5]
    assert top_regressions(base, cand, polarity="lower_better") == [(0, 0.5)]


def test_top_regressions_validates_length():
    with pytest.raises(ValueError):
        top_regressions([1.0, 1.0], [1.0])


def test_describe_includes_samples():
    verdict = Verdict(PASS, 0.4, 0.0, "no meaningful regression", -0.01, 0.01, samples=6)
    assert "6 runs" in describe(verdict)


def test_reports_put_failures_first():
    results = {
        "a_pass": Verdict(PASS, 0.9, 0.01, "ok"),
        "b_fail": Verdict(FAIL, 0.01, -0.3, "regressed"),
        "c_incon": Verdict(INCONCLUSIVE, 0.5, -0.05, "underpowered"),
    }
    text = format_report(results)
    order = [text.index("b_fail"), text.index("c_incon"), text.index("a_pass")]
    assert order == sorted(order)
    md = to_markdown(results)
    assert md.index("b_fail") < md.index("c_incon") < md.index("a_pass")


def test_reports_rank_failures_by_severity():
    results = {
        "small": Verdict(FAIL, 0.01, -0.1, "regressed"),
        "big": Verdict(FAIL, 0.01, -0.4, "regressed"),
    }
    text = format_report(results)
    assert text.index("big") < text.index("small")
