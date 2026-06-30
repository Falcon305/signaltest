import json
from dataclasses import asdict
from html import escape
from pathlib import Path
from typing import Union
from xml.etree.ElementTree import Element, SubElement, tostring

from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS, Verdict

ICON = {PASS: "✅", FAIL: "❌", INCONCLUSIVE: "⚠️"}
COLOR = {PASS: "#1a7f37", FAIL: "#cf222e", INCONCLUSIVE: "#9a6700"}


def describe(verdict: Verdict) -> str:
    detail = verdict.reason
    stats = _stats(verdict)
    return f"{detail} ({stats})" if stats else detail


def _stats(verdict: Verdict) -> str:
    parts = []
    if verdict.effect is not None:
        parts.append(f"effect={verdict.effect:+.3f}")
    if verdict.ci_low is not None and verdict.ci_high is not None:
        parts.append(f"95% CI [{verdict.ci_low:+.3f}, {verdict.ci_high:+.3f}]")
    if verdict.pvalue is not None:
        parts.append(f"p={verdict.pvalue:.3f}")
    if verdict.samples is not None:
        parts.append(f"{verdict.samples} runs")
    return ", ".join(parts)


def ci_bar(verdict: Verdict, width: int = 21) -> str:
    """A Unicode bar showing the effect's 95% CI against zero.

    If the bar straddles the centre mark the interval includes zero (not a clear
    regression); if it sits entirely to one side, zero is excluded.
    """
    if verdict.ci_low is None or verdict.ci_high is None:
        return ""
    mid = (width - 1) // 2
    span = max(abs(verdict.ci_low), abs(verdict.ci_high), 1e-9)

    def position(value: float) -> int:
        return max(0, min(width - 1, round(value / span * mid) + mid))

    low, high = position(verdict.ci_low), position(verdict.ci_high)
    cells = []
    for i in range(width):
        if i == mid:
            cells.append("╋" if low <= i <= high else "│")
        elif low <= i <= high:
            cells.append("━")
        else:
            cells.append("·")
    return "".join(cells)


_SEVERITY = {FAIL: 0, INCONCLUSIVE: 1, PASS: 2}


def _ordered(results: dict[str, Verdict]) -> list[tuple[str, Verdict]]:
    """Worst first: failures, then inconclusive, then passes; biggest drop on top."""

    def rank(item: tuple[str, Verdict]) -> tuple[int, float]:
        verdict = item[1]
        effect = verdict.effect if verdict.effect is not None else float("inf")
        return (_SEVERITY.get(verdict.status, 3), effect)

    return sorted(results.items(), key=rank)


def _counts(results: dict[str, Verdict]) -> dict[str, int]:
    counts = {PASS: 0, FAIL: 0, INCONCLUSIVE: 0}
    for verdict in results.values():
        counts[verdict.status] += 1
    return counts


def _summary(results: dict[str, Verdict]) -> str:
    c = _counts(results)
    return f"{c[PASS]} passed, {c[FAIL]} failed, {c[INCONCLUSIVE]} inconclusive"


def format_report(results: dict[str, Verdict]) -> str:
    lines = []
    for case_id, verdict in _ordered(results):
        lines.append(f"{verdict.status.upper():13} {case_id}: {describe(verdict)}")
    lines.append(_summary(results))
    return "\n".join(lines)


def to_markdown(results: dict[str, Verdict]) -> str:
    lines = [
        "<!-- signaltest -->",
        "### signaltest",
        "",
        "| Case | Status | Detail | 95% CI |",
        "| --- | --- | --- | --- |",
    ]
    for case_id, verdict in _ordered(results):
        icon = ICON.get(verdict.status, "")
        bar = ci_bar(verdict)
        cell = f"`{bar}`" if bar else ""
        lines.append(f"| {case_id} | {icon} {verdict.status} | {describe(verdict)} | {cell} |")
    lines.append("")
    lines.append(f"**{_summary(results)}**")
    return "\n".join(lines)


def to_html(results: dict[str, Verdict]) -> str:
    rows = []
    for case_id, verdict in _ordered(results):
        color = COLOR.get(verdict.status, "#000")
        bar = ci_bar(verdict)
        rows.append(
            f"<tr><td>{escape(case_id)}</td>"
            f'<td style="color:{color};font-weight:600">{verdict.status}</td>'
            f"<td>{escape(describe(verdict))}</td>"
            f'<td style="font-family:monospace">{escape(bar)}</td></tr>'
        )
    body = "\n".join(rows)
    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8"><title>signaltest</title>\n'
        "<style>body{font-family:system-ui,sans-serif;margin:2rem}"
        "table{border-collapse:collapse;width:100%}"
        "th,td{border:1px solid #d0d7de;padding:.4rem .6rem;text-align:left}"
        "th{background:#f6f8fa}</style></head>\n"
        "<body><h2>signaltest</h2>\n"
        "<table><thead><tr><th>Case</th><th>Status</th><th>Detail</th>"
        "<th>95% CI</th></tr></thead>\n"
        f"<tbody>\n{body}\n</tbody></table>\n"
        f"<p><strong>{_summary(results)}</strong></p>\n"
        "</body></html>\n"
    )


def to_junit(results: dict[str, Verdict]) -> str:
    counts = _counts(results)
    suite = Element(
        "testsuite",
        name="signaltest",
        tests=str(len(results)),
        failures=str(counts[FAIL]),
        skipped=str(counts[INCONCLUSIVE]),
    )
    for case_id, verdict in results.items():
        case = SubElement(suite, "testcase", name=case_id, classname="signaltest")
        if verdict.status == FAIL:
            failure = SubElement(case, "failure", message=describe(verdict))
            failure.text = verdict.reason
        elif verdict.status == INCONCLUSIVE:
            SubElement(case, "skipped", message=describe(verdict))
    return '<?xml version="1.0" encoding="utf-8"?>\n' + tostring(suite, encoding="unicode")


def write_json(results: dict[str, Verdict], path: Union[str, Path]) -> None:
    data = {case_id: asdict(verdict) for case_id, verdict in results.items()}
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True))


def read_json(path: Union[str, Path]) -> dict[str, Verdict]:
    raw = json.loads(Path(path).read_text())
    return {case_id: Verdict(**fields) for case_id, fields in raw.items()}


def exit_code(results: dict[str, Verdict]) -> int:
    return 1 if any(v.status == FAIL for v in results.values()) else 0
