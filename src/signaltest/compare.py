from collections.abc import Sequence
from typing import Any, Optional

import numpy as np

from signaltest.metrics.base import HIGHER_BETTER, NUMERIC
from signaltest.stats.effect import effect_ci
from signaltest.stats.gate import Verdict, decide_gate, is_underpowered
from signaltest.stats.power import advise
from signaltest.stats.significance import boolean_significance, numeric_significance

DEFAULT_MIN_EFFECT = {"numeric": 0.03, "boolean": 0.10}


def measure_scores(
    baseline: Sequence[Any],
    candidate: Sequence[Any],
    *,
    kind: str,
    polarity: str,
    min_effect: Optional[float] = None,
    alpha: float = 0.05,
) -> dict[str, Any]:
    resolved = DEFAULT_MIN_EFFECT[kind] if min_effect is None else min_effect
    if kind == NUMERIC:
        pvalue = numeric_significance(baseline, candidate)
    else:
        pvalue = boolean_significance(baseline, candidate)
    ci_low, ci_high = effect_ci(baseline, candidate)
    return {
        "pvalue": pvalue,
        "effect": float(np.mean(candidate) - np.mean(baseline)),
        "polarity": polarity,
        "min_effect": resolved,
        "n_valid": min(len(baseline), len(candidate)),
        "underpowered": is_underpowered(len(baseline), len(candidate), alpha),
        "recommended": advise(baseline, kind, resolved, alpha),
        "ci": (ci_low, ci_high),
    }


def compare_scores(
    baseline: Sequence[Any],
    candidate: Sequence[Any],
    *,
    kind: str = NUMERIC,
    polarity: str = HIGHER_BETTER,
    alpha: float = 0.05,
    min_effect: Optional[float] = None,
    min_valid: int = 2,
) -> Verdict:
    """Gate two raw score arrays, e.g. from Inspect AI epochs or DeepEval trials."""
    n_valid = min(len(baseline), len(candidate))
    if n_valid < min_valid:
        return decide_gate(1.0, 0.0, n_valid=n_valid, min_valid=min_valid)
    stats = measure_scores(
        baseline, candidate, kind=kind, polarity=polarity, min_effect=min_effect, alpha=alpha
    )
    return decide_gate(
        stats["pvalue"],
        stats["effect"],
        polarity=stats["polarity"],
        alpha=alpha,
        min_effect=stats["min_effect"],
        n_valid=stats["n_valid"],
        min_valid=min_valid,
        underpowered=stats["underpowered"],
        recommended_samples=stats["recommended"],
        ci_low=stats["ci"][0],
        ci_high=stats["ci"][1],
    )
