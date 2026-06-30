import json
from dataclasses import asdict
from pathlib import Path
from typing import Union

from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS, Verdict

ICON = {PASS: "✅", FAIL: "❌", INCONCLUSIVE: "⚠️"}


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


def write_json(results: dict[str, Verdict], path: Union[str, Path]) -> None:
    data = {case_id: asdict(verdict) for case_id, verdict in results.items()}
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True))


def read_json(path: Union[str, Path]) -> dict[str, Verdict]:
    raw = json.loads(Path(path).read_text())
    return {case_id: Verdict(**fields) for case_id, fields in raw.items()}


def exit_code(results: dict[str, Verdict]) -> int:
    return 1 if any(v.status == FAIL for v in results.values()) else 0
