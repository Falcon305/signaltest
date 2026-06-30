import numpy as np
from scipy.stats import permutation_test


def numeric_significance(baseline, candidate, rng=0):
    if len(baseline) < 2 or len(candidate) < 2:
        raise ValueError("each group needs at least 2 samples")

    def stat(a, b, axis=0):
        return np.mean(a, axis=axis) - np.mean(b, axis=axis)

    result = permutation_test(
        (baseline, candidate),
        stat,
        permutation_type="independent",
        alternative="two-sided",
        vectorized=True,
        rng=rng,
    )
    return float(result.pvalue)
