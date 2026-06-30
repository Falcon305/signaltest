import json
from pathlib import Path
from typing import Any, Union

from signaltest.report import ICON
from signaltest.stats.gate import Verdict


def append_history(results: dict[str, Verdict], path: Union[str, Path], timestamp: str) -> None:
    line = {
        "time": timestamp,
        "cases": {
            case_id: {"status": v.status, "effect": v.effect, "pvalue": v.pvalue}
            for case_id, v in results.items()
        },
    }
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a") as handle:
        handle.write(json.dumps(line, sort_keys=True) + "\n")


def read_history(path: Union[str, Path]) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    return [json.loads(line) for line in target.read_text().splitlines() if line.strip()]


def format_trends(history: list[dict[str, Any]], width: int = 12) -> str:
    if not history:
        return "no history"
    case_ids: list[str] = []
    for run in history:
        for case_id in run["cases"]:
            if case_id not in case_ids:
                case_ids.append(case_id)
    recent = history[-width:]
    lines = [f"{len(history)} runs"]
    for case_id in case_ids:
        marks = []
        for run in recent:
            entry = run["cases"].get(case_id)
            marks.append(ICON.get(entry["status"], "·") if entry else "·")
        lines.append(f"{case_id}  {''.join(marks)}  {_latest(history, case_id)}")
    return "\n".join(lines)


def _latest(history: list[dict[str, Any]], case_id: str) -> str:
    for run in reversed(history):
        if case_id in run["cases"]:
            return str(run["cases"][case_id]["status"])
    return "—"
