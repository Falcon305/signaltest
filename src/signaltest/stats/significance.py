import numpy as np
from scipy.stats import fisher_exact, permutation_test


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


def boolean_significance(baseline, candidate):
    if len(baseline) < 1 or len(candidate) < 1:
        raise ValueError("each group needs at least 1 sample")
    b_true = sum(1 for x in baseline if x)
    c_true = sum(1 for x in candidate if x)
    table = [[b_true, len(baseline) - b_true], [c_true, len(candidate) - c_true]]
    _, pvalue = fisher_exact(table)
    return float(pvalue)
