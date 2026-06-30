import numpy as np
from scipy.stats import bootstrap


def effect_ci(baseline, candidate, confidence=0.95, rng=0):
    if len(baseline) < 2 or len(candidate) < 2:
        raise ValueError("each group needs at least 2 samples")

    def diff(b, c, axis=0):
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
