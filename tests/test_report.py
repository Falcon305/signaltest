from signaltest.report import exit_code, format_report
from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS, Verdict


def verdict(status):
    return Verdict(status, None, None, "reason")


def test_report_lists_cases_and_summary():
    out = format_report({"a": verdict(PASS), "b": verdict(FAIL)})
    assert "a" in out
    assert "b" in out
    assert "1 passed, 1 failed" in out


def test_exit_code_one_on_failure():
    assert exit_code({"a": verdict(FAIL)}) == 1


def test_exit_code_zero_when_clean():
    assert exit_code({"a": verdict(PASS), "b": verdict(INCONCLUSIVE)}) == 0
