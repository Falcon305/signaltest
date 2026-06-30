import json
from dataclasses import asdict
from html import escape
from pathlib import Path
from typing import Union

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
    if verdict.pvalue is not None:
        parts.append(f"p={verdict.pvalue:.3f}")
    return ", ".join(parts)


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
    for case_id, verdict in results.items():
        lines.append(f"{verdict.status.upper():13} {case_id}: {describe(verdict)}")
    lines.append(_summary(results))
    return "\n".join(lines)


def to_markdown(results: dict[str, Verdict]) -> str:
    lines = [
        "<!-- signaltest -->",
        "### signaltest",
        "",
        "| Case | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for case_id, verdict in results.items():
        icon = ICON.get(verdict.status, "")
        lines.append(f"| {case_id} | {icon} {verdict.status} | {describe(verdict)} |")
    lines.append("")
    lines.append(f"**{_summary(results)}**")
    return "\n".join(lines)


def to_html(results: dict[str, Verdict]) -> str:
    rows = []
    for case_id, verdict in results.items():
        color = COLOR.get(verdict.status, "#000")
        rows.append(
            f"<tr><td>{escape(case_id)}</td>"
            f'<td style="color:{color};font-weight:600">{verdict.status}</td>'
            f"<td>{escape(describe(verdict))}</td></tr>"
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
        "<table><thead><tr><th>Case</th><th>Status</th><th>Detail</th></tr></thead>\n"
        f"<tbody>\n{body}\n</tbody></table>\n"
        f"<p><strong>{_summary(results)}</strong></p>\n"
        "</body></html>\n"
    )


def write_json(results: dict[str, Verdict], path: Union[str, Path]) -> None:
    data = {case_id: asdict(verdict) for case_id, verdict in results.items()}
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True))


def read_json(path: Union[str, Path]) -> dict[str, Verdict]:
    raw = json.loads(Path(path).read_text())
    return {case_id: Verdict(**fields) for case_id, fields in raw.items()}


def exit_code(results: dict[str, Verdict]) -> int:
    return 1 if any(v.status == FAIL for v in results.values()) else 0
