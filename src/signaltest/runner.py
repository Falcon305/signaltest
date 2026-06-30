from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, Union

import numpy as np

from signaltest.baseline.record import key, make_record, update_baseline
from signaltest.baseline.store import BaselineStore
from signaltest.metrics.base import NUMERIC, Metric, Score
from signaltest.report import describe
from signaltest.stats.correction import bh_adjust
from signaltest.stats.gate import FAIL, PASS, Verdict, decide_gate, is_underpowered
from signaltest.stats.significance import boolean_significance, numeric_significance

DEFAULT_MIN_EFFECT = {"numeric": 0.03, "boolean": 0.10}


@dataclass
class Case:
    case_id: str
    run: Callable[[], Any]
    expected: Any
    metric: Metric


def collect_scores(case: Case, n: int) -> list[Optional[Score]]:
    scores: list[Optional[Score]] = []
    for _ in range(n):
        try:
            scores.append(case.metric.score(case.run(), case.expected))
        except Exception:
            scores.append(None)
    return scores


def _measure(
    case: Case,
    store: BaselineStore,
    n: int,
    alpha: float,
    min_valid: int,
    min_effect: Optional[float],
    model: Optional[str],
) -> Union[Verdict, dict[str, Any]]:
    candidate = [s for s in collect_scores(case, n) if s is not None]
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

    if case.metric.kind == NUMERIC:
        pvalue = numeric_significance(baseline, candidate)
    else:
        pvalue = boolean_significance(baseline, candidate)

    return {
        "pvalue": pvalue,
        "effect": float(np.mean(candidate) - np.mean(baseline)),
        "polarity": case.metric.polarity,
        "min_effect": DEFAULT_MIN_EFFECT[case.metric.kind] if min_effect is None else min_effect,
        "n_valid": n_valid,
        "underpowered": is_underpowered(len(baseline), len(candidate), alpha),
    }


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
    )


def check_case(
    case: Case,
    store: BaselineStore,
    n: int = 10,
    alpha: float = 0.05,
    min_effect: Optional[float] = None,
    min_valid: int = 2,
    model: Optional[str] = None,
) -> Verdict:
    measured = _measure(case, store, n, alpha, min_valid, min_effect, model)
    if isinstance(measured, Verdict):
        return measured
    return _decide(measured, alpha, min_valid)


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
) -> dict[str, Verdict]:
    store = BaselineStore(baseline_path)
    results: dict[str, Verdict] = {}
    pending = []
    for case in cases:
        measured = _measure(case, store, n, alpha, min_valid, min_effect, model)
        if isinstance(measured, Verdict):
            results[case.case_id] = measured
        else:
            pending.append((case, measured))

    adjusted = bh_adjust([stats["pvalue"] for _, stats in pending])
    for (case, stats), pvalue in zip(pending, adjusted):
        stats = {**stats, "pvalue": pvalue}
        results[case.case_id] = _decide(stats, alpha, min_valid)
    return results
