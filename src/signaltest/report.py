from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS


def format_report(results):
    counts = {PASS: 0, FAIL: 0, INCONCLUSIVE: 0}
    lines = []
    for case_id, verdict in results.items():
        counts[verdict.status] += 1
        lines.append(f"{verdict.status.upper():13} {case_id}: {verdict.reason}")
    lines.append(f"{counts[PASS]} passed, {counts[FAIL]} failed, {counts[INCONCLUSIVE]} inconclusive")
    return "\n".join(lines)


def exit_code(results):
    return 1 if any(v.status == FAIL for v in results.values()) else 0
