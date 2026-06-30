from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from math import sqrt
from typing import Any, Callable, Optional

from scipy.stats import norm

from signaltest.compare import measure_scores
from signaltest.stats.gate import FAIL, PASS, Verdict, decide_gate
from signaltest.stats.significance import PERMUTATION

POCOCK = "pocock"
OBRIEN_FLEMING = "obrien_fleming"


def alpha_schedule(alpha: float, looks: int, spending: str = OBRIEN_FLEMING) -> list[float]:
    """Per-look nominal alphas that sum to `alpha`.

    Any allocation summing to `alpha` keeps the union-bound guarantee regardless of
    how the looks correlate. O'Brien-Fleming spends almost nothing early and saves
    most of the budget for the final look, so stopping early needs strong evidence
    but the final decision keeps nearly full power; Pocock spreads it evenly.
    """
    if looks < 1:
        raise ValueError("looks must be >= 1")
    if spending == POCOCK:
        return [alpha / looks] * looks
    if spending != OBRIEN_FLEMING:
        raise ValueError(f"unknown spending function: {spending}")
    z = norm.ppf(1 - alpha / 2)
    cumulative = [float(2 - 2 * norm.cdf(z / sqrt((k + 1) / looks))) for k in range(looks)]
    return [cumulative[0]] + [cumulative[k] - cumulative[k - 1] for k in range(1, looks)]


def sample_schedule(min_n: int, max_n: int, looks: int) -> list[int]:
    """Cumulative sample sizes for each interim look, from min_n up to max_n."""
    if looks < 1:
        raise ValueError("looks must be >= 1")
    if min_n < 2:
        raise ValueError("min_n must be >= 2")
    if max_n < min_n:
        raise ValueError("max_n must be >= min_n")
    if looks == 1:
        return [max_n]
    step = (max_n - min_n) / (looks - 1)
    sizes = sorted({int(round(min_n + step * i)) for i in range(looks)})
    sizes[-1] = max_n
    return sizes


def sequential_gate(
    baseline: Sequence[Any],
    sampler: Callable[[], Optional[Any]],
    *,
    kind: str,
    polarity: str = "higher_better",
    sizes: Sequence[int],
    alpha: float = 0.05,
    min_effect: Optional[float] = None,
    test: str = PERMUTATION,
    comparisons: int = 1,
    spending: str = OBRIEN_FLEMING,
    workers: int = 1,
) -> Verdict:
    """Draw candidate samples in batches, stopping as soon as the gate is conclusive.

    Alpha is spent across the looks (so peeking does not inflate false positives)
    and across `comparisons` cases (so a suite of sequential gates keeps suite-wide
    false positives bounded). A PASS can still be reached early once the effect CI
    sits within the no-meaningful-regression threshold. Each look's batch is drawn
    with `workers` threads; the draw order is preserved, so the verdict is the same
    as running single-threaded.
    """
    schedule = alpha_schedule(alpha, len(sizes), spending)
    drawn: list[Optional[Any]] = []
    stats: Optional[dict[str, Any]] = None
    alpha_k = schedule[-1] / comparisons
    for i, target in enumerate(sizes):
        if len(drawn) < target:
            drawn.extend(_draw(sampler, target - len(drawn), workers))
        candidate = [s for s in drawn if s is not None]
        if len(candidate) < 2:
            continue
        alpha_k = schedule[i] / comparisons
        stats = measure_scores(
            baseline,
            candidate,
            kind=kind,
            polarity=polarity,
            min_effect=min_effect,
            alpha=alpha_k,
            test=test,
        )
        early = _fail(stats, alpha_k) or _rope_pass(stats, polarity)
        if early is not None:
            early.samples = len(drawn)
            return early
    valid = len([s for s in drawn if s is not None])
    if stats is None:
        verdict = decide_gate(1.0, 0.0, n_valid=valid, min_valid=2)
    else:
        verdict = _final(stats, alpha_k)
    verdict.samples = len(drawn)
    return verdict


def _draw(sampler: Callable[[], Optional[Any]], count: int, workers: int) -> list[Optional[Any]]:
    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(lambda _: sampler(), range(count)))
    return [sampler() for _ in range(count)]


def _fail(stats: dict[str, Any], alpha: float) -> Optional[Verdict]:
    verdict = decide_gate(
        stats["pvalue"],
        stats["effect"],
        polarity=stats["polarity"],
        alpha=alpha,
        min_effect=stats["min_effect"],
        n_valid=stats["n_valid"],
        min_valid=2,
        underpowered=False,
        ci_low=stats["ci"][0],
        ci_high=stats["ci"][1],
    )
    return verdict if verdict.status == FAIL else None


def _rope_pass(stats: dict[str, Any], polarity: str) -> Optional[Verdict]:
    low, high = stats["ci"]
    margin = stats["min_effect"]
    clear = low > -margin if polarity == "higher_better" else high < margin
    if not clear:
        return None
    return Verdict(
        PASS,
        stats["pvalue"],
        stats["effect"],
        "no meaningful regression (CI within threshold)",
        low,
        high,
    )


def _final(stats: dict[str, Any], alpha: float) -> Verdict:
    return decide_gate(
        stats["pvalue"],
        stats["effect"],
        polarity=stats["polarity"],
        alpha=alpha,
        min_effect=stats["min_effect"],
        n_valid=stats["n_valid"],
        min_valid=2,
        underpowered=stats["underpowered"],
        recommended_samples=stats["recommended"],
        ci_low=stats["ci"][0],
        ci_high=stats["ci"][1],
    )
