from signaltest.history import append_history, format_trends, read_history
from signaltest.stats.gate import FAIL, PASS, Verdict


def test_append_then_read(tmp_path):
    path = tmp_path / "h.jsonl"
    append_history({"math": Verdict(PASS, 1.0, 0.0, "ok")}, path, "2026-06-30T10:00:00")
    append_history({"math": Verdict(FAIL, 0.01, -0.2, "bad")}, path, "2026-06-30T11:00:00")
    runs = read_history(path)
    assert len(runs) == 2
    assert runs[0]["cases"]["math"]["status"] == "pass"
    assert runs[1]["cases"]["math"]["effect"] == -0.2


def test_read_missing_file_is_empty(tmp_path):
    assert read_history(tmp_path / "nope.jsonl") == []


def test_format_trends_shows_marks_and_latest(tmp_path):
    path = tmp_path / "h.jsonl"
    append_history({"math": Verdict(PASS, 1.0, 0.0, "ok")}, path, "t1")
    append_history({"math": Verdict(FAIL, 0.01, -0.2, "bad")}, path, "t2")
    out = format_trends(read_history(path))
    assert "2 runs" in out
    assert "math" in out
    assert "✅" in out and "❌" in out
    assert out.strip().endswith("fail")


def test_format_trends_handles_missing_case(tmp_path):
    path = tmp_path / "h.jsonl"
    append_history({"a": Verdict(PASS, 1.0, 0.0, "ok")}, path, "t1")
    append_history({"b": Verdict(PASS, 1.0, 0.0, "ok")}, path, "t2")
    out = format_trends(read_history(path))
    assert "·" in out  # a is absent from the second run


def test_format_trends_empty():
    assert format_trends([]) == "no history"


def test_latest_fallback_for_unknown_case():
    from signaltest.history import _latest

    assert _latest([], "ghost") == "—"
