import asyncio
import inspect
import os
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, Union

from signaltest import config as cfg
from signaltest.baseline.cache import ScoreCache
from signaltest.baseline.record import key, make_record, update_baseline
from signaltest.baseline.store import BaselineStore
from signaltest.compare import measure_scores
from signaltest.metrics.base import Metric, Score
from signaltest.report import describe
from signaltest.results import collector
from signaltest.stats.correction import bh_adjust
from signaltest.stats.gate import FAIL, PASS, Verdict, decide_gate
from signaltest.stats.sequential import OBRIEN_FLEMING, sample_schedule, sequential_gate
from signaltest.stats.significance import PERMUTATION

_UNSET: Any = object()


@dataclass
class Case:
    case_id: str
    run: Callable[[], Any]
    expected: Any
    metric: Metric
    cache_key: Optional[str] = None


def _sample(case: Case) -> Optional[Score]:
    try:
        output = case.run()
        if inspect.iscoroutine(output):
            output = asyncio.run(output)
        return case.metric.score(output, case.expected)
    except Exception:
        return None


def collect_scores(
    case: Case, n: int, cache: Optional[ScoreCache] = None, workers: int = 1
) -> list[Optional[Score]]:
    ckey: Optional[str] = None
    if cache is not None and case.cache_key is not None:
        ckey = f"{case.cache_key}::{case.metric.name}::n{n}"
        cached = cache.get(ckey)
        if cached is not None:
            return cached
    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            scores = list(pool.map(lambda _: _sample(case), range(n)))
    else:
        scores = [_sample(case) for _ in range(n)]
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
    update: bool = False,
    workers: int = 1,
    test: str = PERMUTATION,
    sequential: bool = False,
    max_n: Optional[int] = None,
    looks: int = 4,
    comparisons: int = 1,
    spending: str = OBRIEN_FLEMING,
) -> Union[Verdict, dict[str, Any]]:
    k = key(case.case_id, case.metric.name)
    data = store.load()

    is_cold = k not in data
    if update or is_cold or data[k].get("model") != model:
        candidate = [s for s in collect_scores(case, n, cache, workers) if s is not None]
        update_baseline(store, k, make_record(candidate, model=model))
        if update:
            reason = "updated baseline"
        elif is_cold:
            reason = "recorded baseline (cold start)"
        else:
            reason = "re-recorded baseline (model changed)"
        return Verdict(PASS, None, None, reason)

    baseline = data[k]["scores"]
    if sequential:
        if len(baseline) < min_valid:
            return decide_gate(1.0, 0.0, n_valid=len(baseline), min_valid=min_valid)
        cap = max_n if max_n is not None else n * 3
        sizes = sample_schedule(n, max(cap, n), looks)
        return sequential_gate(
            baseline,
            lambda: _sample(case),
            kind=case.metric.kind,
            polarity=case.metric.polarity,
            sizes=sizes,
            alpha=alpha,
            min_effect=min_effect,
            test=test,
            comparisons=comparisons,
            spending=spending,
        )

    candidate = [s for s in collect_scores(case, n, cache, workers) if s is not None]
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
        test=test,
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
        ci_low=stats["ci"][0],
        ci_high=stats["ci"][1],
    )


def check_case(
    case: Case,
    store: BaselineStore,
    n: Optional[int] = None,
    alpha: Optional[float] = None,
    min_effect: Any = _UNSET,
    min_valid: Optional[int] = None,
    model: Optional[str] = None,
    cache: Optional[Union[str, Path]] = None,
    update: bool = False,
    workers: Optional[int] = None,
    test: Optional[str] = None,
    sequential: Optional[bool] = None,
    max_n: Optional[int] = None,
    looks: Optional[int] = None,
    spending: Optional[str] = None,
) -> Verdict:
    n = cfg.get("n") if n is None else n
    alpha = cfg.get("alpha") if alpha is None else alpha
    min_effect = cfg.get("min_effect") if min_effect is _UNSET else min_effect
    min_valid = cfg.get("min_valid") if min_valid is None else min_valid
    workers = cfg.get("workers") if workers is None else workers
    test = cfg.get("test") if test is None else test
    sequential = cfg.get("sequential") if sequential is None else sequential
    max_n = cfg.get("max_n") if max_n is None else max_n
    looks = cfg.get("looks") if looks is None else looks
    spending = cfg.get("spending") if spending is None else spending
    score_cache = ScoreCache(cache) if cache is not None else None
    measured = _measure(
        case,
        store,
        n,
        alpha,
        min_valid,
        min_effect,
        model,
        score_cache,
        _update(update),
        workers,
        test,
        sequential,
        max_n,
        looks,
        1,
        spending,
    )
    verdict = measured if isinstance(measured, Verdict) else _decide(measured, alpha, min_valid)
    collector.record(case.case_id, verdict)
    return verdict


def _update(update: bool) -> bool:
    return update or os.environ.get("SIGNALTEST_UPDATE") == "1"


def assert_no_regression(case: Case, baseline_path: Union[str, Path], **kwargs: Any) -> Verdict:
    verdict = check_case(case, BaselineStore(baseline_path), **kwargs)
    if verdict.status == FAIL:
        raise AssertionError(f"regression in {case.case_id}: {describe(verdict)}")
    return verdict


def run_suite(
    cases: Sequence[Case],
    baseline_path: Union[str, Path],
    n: Optional[int] = None,
    alpha: Optional[float] = None,
    min_effect: Any = _UNSET,
    min_valid: Optional[int] = None,
    model: Optional[str] = None,
    cache: Optional[Union[str, Path]] = None,
    update: bool = False,
    workers: Optional[int] = None,
    test: Optional[str] = None,
    sequential: Optional[bool] = None,
    max_n: Optional[int] = None,
    looks: Optional[int] = None,
    spending: Optional[str] = None,
) -> dict[str, Verdict]:
    n = cfg.get("n") if n is None else n
    alpha = cfg.get("alpha") if alpha is None else alpha
    min_effect = cfg.get("min_effect") if min_effect is _UNSET else min_effect
    min_valid = cfg.get("min_valid") if min_valid is None else min_valid
    workers = cfg.get("workers") if workers is None else workers
    test = cfg.get("test") if test is None else test
    sequential = cfg.get("sequential") if sequential is None else sequential
    max_n = cfg.get("max_n") if max_n is None else max_n
    looks = cfg.get("looks") if looks is None else looks
    spending = cfg.get("spending") if spending is None else spending
    store = BaselineStore(baseline_path)
    score_cache = ScoreCache(cache) if cache is not None else None
    do_update = _update(update)
    results: dict[str, Verdict] = {}
    pending = []
    for case in cases:
        measured = _measure(
            case,
            store,
            n,
            alpha,
            min_valid,
            min_effect,
            model,
            score_cache,
            do_update,
            workers,
            test,
            sequential,
            max_n,
            looks,
            len(cases),
            spending,
        )
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
