from collections.abc import Sequence
from typing import Any

from signaltest.trajectory.model import Step


def match_score(
    baseline: Sequence[Step], candidate: Sequence[Step], ignore_keys: Sequence[str] = ()
) -> float:
    steps = max(len(baseline), len(candidate))
    if steps == 0:
        return 1.0
    matched = sum(
        b.tool == c.tool and _without(b.args, ignore_keys) == _without(c.args, ignore_keys)
        for b, c in zip(baseline, candidate)
    )
    return matched / steps


def _without(args: dict[str, Any], ignore_keys: Sequence[str]) -> dict[str, Any]:
    return {k: v for k, v in args.items() if k not in ignore_keys}
