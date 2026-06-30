from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, Union

from signaltest.baseline.cache import ScoreCache
from signaltest.baseline.record import key, make_record, update_baseline
from signaltest.baseline.store import BaselineStore
from signaltest.compare import measure_scores
from signaltest.metrics.base import Metric, Score
from signaltest.report import describe
from signaltest.results import collector
from signaltest.stats.correction import bh_adjust
from signaltest.stats.gate import FAIL, PASS, Verdict, decide_gate


@dataclass
class Case:
    case_id: str
    run: Callable[[], Any]
    expected: Any
    metric: Metric
    cache_key: Optional[str] = None


def collect_scores(case: Case, n: int, cache: Optional[ScoreCache] = None) -> list[Optional[Score]]:
    ckey: Optional[str] = None
    if cache is not None and case.cache_key is not None:
        ckey = f"{case.cache_key}::{case.metric.name}::n{n}"
        cached = cache.get(ckey)
        if cached is not None:
            return cached
    scores: list[Optional[Score]] = []
    for _ in range(n):
        try:
            scores.append(case.metric.score(case.run(), case.expected))
        except Exception:
            scores.append(None)
    if cache is not None and ckey is not None:
        cache.put(ckey, scores)
    return scores


def _measure(
    case: Case,
    store: BaselineStore,
    n: int,
    alpha: float,
    min_valid: int,
    min_effect: Optional[float],
    model: Optional[str],
    cache: Optional[ScoreCache] = None,
) -> Union[Verdict, dict[str, Any]]:
    candidate = [s for s in collect_scores(case, n, cache) if s is not None]
    k = key(case.case_id, case.metric.name)
    data = store.load()

    is_cold = k not in data
    if is_cold or data[k].get("model") != model:
        update_baseline(store, k, make_record(candidate, model=model))
        reason = (
            "recorded baseline (cold start)" if is_cold else "re-recorded baseline (model changed)"
        )
        return Verdict(PASS, None, None, reason)

    baseline = data[k]["scores"]
    n_valid = min(len(baseline), len(candidate))
    if n_valid < min_valid:
        return decide_gate(1.0, 0.0, n_valid=n_valid, min_valid=min_valid)

    return measure_scores(
        baseline,
        candidate,
        kind=case.metric.kind,
        polarity=case.metric.polarity,
        min_effect=min_effect,
        alpha=alpha,
    )


def _decide(stats: dict[str, Any], alpha: float, min_valid: int) -> Verdict:
    return decide_gate(
        stats["pvalue"],
        stats["effect"],
        polarity=stats["polarity"],
        alpha=alpha,
        min_effect=stats["min_effect"],
        n_valid=stats["n_valid"],
        min_valid=min_valid,
        underpowered=stats["underpowered"],
        recommended_samples=stats["recommended"],
    )


def check_case(
    case: Case,
    store: BaselineStore,
    n: int = 10,
    alpha: float = 0.05,
    min_effect: Optional[float] = None,
    min_valid: int = 2,
    model: Optional[str] = None,
    cache: Optional[Union[str, Path]] = None,
) -> Verdict:
    score_cache = ScoreCache(cache) if cache is not None else None
    measured = _measure(case, store, n, alpha, min_valid, min_effect, model, score_cache)
    verdict = measured if isinstance(measured, Verdict) else _decide(measured, alpha, min_valid)
    collector.record(case.case_id, verdict)
    return verdict


def assert_no_regression(case: Case, baseline_path: Union[str, Path], **kwargs: Any) -> Verdict:
    verdict = check_case(case, BaselineStore(baseline_path), **kwargs)
    if verdict.status == FAIL:
        raise AssertionError(f"regression in {case.case_id}: {describe(verdict)}")
    return verdict


def run_suite(
    cases: Sequence[Case],
    baseline_path: Union[str, Path],
    n: int = 10,
    alpha: float = 0.05,
    min_effect: Optional[float] = None,
    min_valid: int = 2,
    model: Optional[str] = None,
    cache: Optional[Union[str, Path]] = None,
) -> dict[str, Verdict]:
    store = BaselineStore(baseline_path)
    score_cache = ScoreCache(cache) if cache is not None else None
    results: dict[str, Verdict] = {}
    pending = []
    for case in cases:
        measured = _measure(case, store, n, alpha, min_valid, min_effect, model, score_cache)
        if isinstance(measured, Verdict):
            results[case.case_id] = measured
        else:
            pending.append((case, measured))

    adjusted = bh_adjust([stats["pvalue"] for _, stats in pending])
    for (case, stats), pvalue in zip(pending, adjusted):
        stats = {**stats, "pvalue": pvalue}
        results[case.case_id] = _decide(stats, alpha, min_valid)
    for case_id, verdict in results.items():
        collector.record(case_id, verdict)
    return results
