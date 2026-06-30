from signaltest.report import describe, format_report
from signaltest.stats.gate import FAIL, PASS, Verdict


def test_describe_includes_effect_and_pvalue():
    verdict = Verdict(FAIL, pvalue=0.003, effect=-0.12, reason="significant regression")
    text = describe(verdict)
    assert "effect=-0.120" in text
    assert "p=0.003" in text


def test_describe_includes_confidence_interval():
    verdict = Verdict(FAIL, pvalue=0.003, effect=-0.12, reason="r", ci_low=-0.21, ci_high=-0.05)
    text = describe(verdict)
    assert "95% CI [-0.210, -0.050]" in text


def test_describe_omits_missing_stats():
    verdict = Verdict(PASS, pvalue=None, effect=None, reason="recorded baseline")
    assert describe(verdict) == "recorded baseline"


def test_report_shows_numbers_for_failures():
    results = {"case": Verdict(FAIL, pvalue=0.01, effect=-0.2, reason="regression")}
    report = format_report(results)
    assert "effect=-0.200" in report
    assert "p=0.010" in report
