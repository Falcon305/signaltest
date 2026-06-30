from collections.abc import Sequence
from typing import Any, Callable, Optional

from signaltest.compare import measure_scores
from signaltest.stats.gate import FAIL, PASS, Verdict, decide_gate
from signaltest.stats.significance import PERMUTATION


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
) -> Verdict:
    """Draw candidate samples in batches, stopping as soon as the gate is conclusive.

    Alpha is spent across the looks (Bonferroni) so peeking does not inflate false
    positives, and across `comparisons` cases so a suite of sequential gates keeps
    suite-wide false positives bounded. A PASS can still be reached early once the
    effect CI sits within the no-meaningful-regression threshold.
    """
    looks = len(sizes)
    alpha_k = alpha / (looks * comparisons)
    drawn: list[Optional[Any]] = []
    stats: Optional[dict[str, Any]] = None
    for target in sizes:
        while len(drawn) < target:
            drawn.append(sampler())
        candidate = [s for s in drawn if s is not None]
        if len(candidate) < 2:
            continue
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
