from signaltest.report import read_json, to_html, to_markdown, write_json
from signaltest.results import collector
from signaltest.stats.gate import FAIL, PASS, Verdict


def test_to_markdown_has_table_and_marker():
    results = {
        "math": Verdict(FAIL, pvalue=0.004, effect=-0.18, reason="regression"),
        "geo": Verdict(PASS, pvalue=None, effect=None, reason="no significant regression"),
    }
    md = to_markdown(results)
    assert "<!-- signaltest -->" in md
    assert "| Case | Status | Detail |" in md
    assert "❌ fail" in md
    assert "✅ pass" in md
    assert "**1 passed, 1 failed, 0 inconclusive**" in md


def test_to_html_is_a_standalone_document():
    results = {
        "math": Verdict(FAIL, pvalue=0.004, effect=-0.18, reason="regression"),
        "geo": Verdict(PASS, pvalue=None, effect=None, reason="no significant regression"),
    }
    html = to_html(results)
    assert html.startswith("<!doctype html>")
    assert "<table>" in html
    assert "math" in html
    assert "#cf222e" in html  # fail color
    assert "1 passed, 1 failed, 0 inconclusive" in html


def test_to_html_escapes_case_ids():
    results = {"<script>": Verdict(PASS, None, None, "ok")}
    html = to_html(results)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_write_then_read_roundtrip(tmp_path):
    results = {"math": Verdict(FAIL, pvalue=0.01, effect=-0.2, reason="regression")}
    path = tmp_path / "results.json"
    write_json(results, path)
    loaded = read_json(path)
    assert loaded == results


def test_collector_records_from_run_suite(tmp_path):
    from signaltest.metrics.exact import ExactMatch
    from signaltest.runner import Case, run_suite

    collector.reset()
    case = Case("c", run=lambda: "4", expected="4", metric=ExactMatch())
    path = tmp_path / "b.json"
    run_suite([case], path, n=6)
    run_suite([case], path, n=6)
    assert "c" in collector.results
