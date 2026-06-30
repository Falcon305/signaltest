from collections.abc import Sequence
from math import ceil

import numpy as np
from scipy.stats import norm

from signaltest.metrics.base import NUMERIC


def samples_for_effect(
    std: float, min_effect: float, alpha: float = 0.05, power: float = 0.8
) -> int:
    """Samples per group to detect a mean shift of `min_effect` given `std`."""
    if min_effect <= 0 or std <= 0:
        return 2
    z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    n = 2 * (z**2) * (std**2) / (min_effect**2)
    return max(2, int(ceil(n)))


def samples_for_paired(
    std_diff: float, min_effect: float, alpha: float = 0.05, power: float = 0.8
) -> int:
    """Pairs needed to detect a mean paired difference of `min_effect`."""
    if min_effect <= 0 or std_diff <= 0:
        return 2
    z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    n = (z**2) * (std_diff**2) / (min_effect**2)
    return max(2, int(ceil(n)))


def samples_for_proportion(
    rate: float, min_effect: float, alpha: float = 0.05, power: float = 0.8
) -> int:
    """Samples per group to detect a `min_effect` change in a pass rate."""
    if min_effect <= 0:
        return 2
    p1 = min(max(rate, 0.0), 1.0)
    p2 = min(max(p1 - min_effect, 0.0), 1.0)
    z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    spread = p1 * (1 - p1) + p2 * (1 - p2)
    n = (z**2) * spread / (min_effect**2)
    return max(2, int(ceil(n)))


def advise(
    baseline: Sequence[float],
    kind: str,
    min_effect: float,
    alpha: float = 0.05,
    power: float = 0.8,
) -> int:
    if kind == NUMERIC:
        std = float(np.std(baseline, ddof=1)) if len(baseline) > 1 else 0.0
        return samples_for_effect(std, min_effect, alpha, power)
    rate = float(np.mean(baseline)) if len(baseline) else 0.0
    return samples_for_proportion(rate, min_effect, alpha, power)
