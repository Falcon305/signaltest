from collections.abc import Sequence
from typing import Any, Optional

import numpy as np

from signaltest.metrics.base import HIGHER_BETTER, NUMERIC
from signaltest.stats.effect import effect_ci, effect_ci_paired
from signaltest.stats.gate import Verdict, decide_gate, is_underpowered, is_underpowered_paired
from signaltest.stats.power import advise, samples_for_paired
from signaltest.stats.significance import (
    PERMUTATION,
    boolean_significance,
    numeric_significance,
    paired_significance,
)

DEFAULT_MIN_EFFECT = {"numeric": 0.03, "boolean": 0.10}


def measure_scores(
    baseline: Sequence[Any],
    candidate: Sequence[Any],
    *,
    kind: str,
    polarity: str,
    min_effect: Optional[float] = None,
    alpha: float = 0.05,
    test: str = PERMUTATION,
    paired: bool = False,
) -> dict[str, Any]:
    resolved = DEFAULT_MIN_EFFECT[kind] if min_effect is None else min_effect
    if paired:
        return _measure_paired(baseline, candidate, kind, polarity, resolved, alpha)
    if kind == NUMERIC:
        pvalue = numeric_significance(baseline, candidate, test=test)
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


def _measure_paired(
    baseline: Sequence[Any],
    candidate: Sequence[Any],
    kind: str,
    polarity: str,
    resolved: float,
    alpha: float,
) -> dict[str, Any]:
    if kind != NUMERIC:
        raise ValueError("paired comparison requires numeric scores")
    diffs = np.asarray(candidate, dtype=float) - np.asarray(baseline, dtype=float)
    std = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0
    ci_low, ci_high = effect_ci_paired(baseline, candidate)
    return {
        "pvalue": paired_significance(baseline, candidate),
        "effect": float(diffs.mean()),
        "polarity": polarity,
        "min_effect": resolved,
        "n_valid": len(diffs),
        "underpowered": is_underpowered_paired(len(diffs), alpha),
        "recommended": samples_for_paired(std, resolved, alpha),
        "ci": (ci_low, ci_high),
    }


def top_regressions(
    baseline: Sequence[Any],
    candidate: Sequence[Any],
    *,
    k: int = 5,
    polarity: str = HIGHER_BETTER,
) -> list[tuple[int, float]]:
    """The inputs that dropped most, as (index, delta) pairs, worst first.

    Pass matched per-input scores (same order); use it to show which examples
    drove a regression instead of only the aggregate verdict.
    """
    if len(baseline) != len(candidate):
        raise ValueError("top_regressions needs equal-length samples")
    deltas = [(i, float(c) - float(b)) for i, (b, c) in enumerate(zip(baseline, candidate))]
    worse = [d for d in deltas if (d[1] < 0 if polarity == HIGHER_BETTER else d[1] > 0)]
    worse.sort(key=lambda d: d[1] if polarity == HIGHER_BETTER else -d[1])
    return worse[:k]


def compare_scores(
    baseline: Sequence[Any],
    candidate: Sequence[Any],
    *,
    kind: str = NUMERIC,
    polarity: str = HIGHER_BETTER,
    alpha: float = 0.05,
    min_effect: Optional[float] = None,
    min_valid: int = 2,
    test: str = PERMUTATION,
    paired: bool = False,
) -> Verdict:
    """Gate two raw score arrays, e.g. from Inspect AI epochs or DeepEval trials.

    Set paired=True when both arrays score the same inputs in the same order;
    the matched comparison removes between-input variance and needs fewer samples.
    """
    n_valid = min(len(baseline), len(candidate))
    if n_valid < min_valid:
        return decide_gate(1.0, 0.0, n_valid=n_valid, min_valid=min_valid)
    stats = measure_scores(
        baseline,
        candidate,
        kind=kind,
        polarity=polarity,
        min_effect=min_effect,
        alpha=alpha,
        test=test,
        paired=paired,
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
