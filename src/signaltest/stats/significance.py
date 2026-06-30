from collections.abc import Sequence
from typing import Any

import numpy as np
from scipy.stats import fisher_exact, mannwhitneyu, permutation_test

PERMUTATION = "permutation"
MANNWHITNEY = "mannwhitney"


def numeric_significance(
    baseline: Sequence[float],
    candidate: Sequence[float],
    rng: int = 0,
    test: str = PERMUTATION,
) -> float:
    if len(baseline) < 2 or len(candidate) < 2:
        raise ValueError("each group needs at least 2 samples")

    if test == MANNWHITNEY:
        return float(mannwhitneyu(candidate, baseline, alternative="two-sided").pvalue)

    def stat(a: Any, b: Any, axis: int = 0) -> Any:
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


def boolean_significance(baseline: Sequence[Any], candidate: Sequence[Any]) -> float:
    if len(baseline) < 1 or len(candidate) < 1:
        raise ValueError("each group needs at least 1 sample")
    b_true = sum(1 for x in baseline if x)
    c_true = sum(1 for x in candidate if x)
    table = [[b_true, len(baseline) - b_true], [c_true, len(candidate) - c_true]]
    _, pvalue = fisher_exact(table)
    return float(pvalue)
