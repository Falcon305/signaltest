from collections.abc import Sequence
from typing import Any

import numpy as np
from scipy.stats import bootstrap


def effect_ci(
    baseline: Sequence[float],
    candidate: Sequence[float],
    confidence: float = 0.95,
    rng: int = 0,
) -> tuple[float, float]:
    if len(baseline) < 2 or len(candidate) < 2:
        raise ValueError("each group needs at least 2 samples")

    def diff(b: Any, c: Any, axis: int = 0) -> Any:
        return np.mean(c, axis=axis) - np.mean(b, axis=axis)

    base = np.asarray(baseline, dtype=float)
    cand = np.asarray(candidate, dtype=float)
    observed = float(cand.mean() - base.mean())
    if np.ptp(base) == 0 and np.ptp(cand) == 0:
        return (observed, observed)

    result = bootstrap(
        (base, cand),
        diff,
        confidence_level=confidence,
        method="percentile",
        vectorized=True,
        rng=rng,
    )
    ci = result.confidence_interval
    return (float(ci.low), float(ci.high))


def effect_ci_paired(
    baseline: Sequence[float],
    candidate: Sequence[float],
    confidence: float = 0.95,
    rng: int = 0,
) -> tuple[float, float]:
    if len(baseline) != len(candidate):
        raise ValueError("paired CI needs equal-length samples")
    if len(baseline) < 2:
        raise ValueError("each group needs at least 2 samples")

    def mean(d: Any, axis: int = 0) -> Any:
        return np.mean(d, axis=axis)

    diffs = np.asarray(candidate, dtype=float) - np.asarray(baseline, dtype=float)
    observed = float(diffs.mean())
    if np.ptp(diffs) == 0:
        return (observed, observed)

    result = bootstrap(
        (diffs,),
        mean,
        confidence_level=confidence,
        method="percentile",
        vectorized=True,
        rng=rng,
    )
    ci = result.confidence_interval
    return (float(ci.low), float(ci.high))
