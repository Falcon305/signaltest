from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS, Verdict


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


def format_report(results: dict[str, Verdict]) -> str:
    counts = {PASS: 0, FAIL: 0, INCONCLUSIVE: 0}
    lines = []
    for case_id, verdict in results.items():
        counts[verdict.status] += 1
        lines.append(f"{verdict.status.upper():13} {case_id}: {describe(verdict)}")
    lines.append(
        f"{counts[PASS]} passed, {counts[FAIL]} failed, {counts[INCONCLUSIVE]} inconclusive"
    )
    return "\n".join(lines)


def exit_code(results: dict[str, Verdict]) -> int:
    return 1 if any(v.status == FAIL for v in results.values()) else 0
