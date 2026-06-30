from collections.abc import Sequence

from scipy.stats import false_discovery_control


def bh_adjust(pvalues: Sequence[float]) -> list[float]:
    if len(pvalues) == 0:
        return []
    adjusted = false_discovery_control(pvalues, method="bh")
    return [float(p) for p in adjusted]
