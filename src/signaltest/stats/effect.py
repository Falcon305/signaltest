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

    result = bootstrap(
        (baseline, candidate),
        diff,
        confidence_level=confidence,
        vectorized=True,
        rng=rng,
    )
    ci = result.confidence_interval
    return (float(ci.low), float(ci.high))
