from dataclasses import dataclass
from typing import Any, Callable

import numpy as np

from signaltest.baseline.record import key, make_record, update_baseline
from signaltest.baseline.store import BaselineStore
from signaltest.metrics.base import NUMERIC
from signaltest.stats.gate import FAIL, PASS, Verdict, decide_gate, is_underpowered
from signaltest.stats.significance import boolean_significance, numeric_significance

DEFAULT_MIN_EFFECT = {"numeric": 0.03, "boolean": 0.10}


@dataclass
class Case:
    case_id: str
    run: Callable[[], Any]
    expected: Any
    metric: Any


def collect_scores(case, n):
    scores = []
    for _ in range(n):
        try:
            scores.append(case.metric.score(case.run(), case.expected))
        except Exception:
            scores.append(None)
    return scores


def check_case(case, store, n=10, alpha=0.05, min_effect=None, min_valid=2):
    candidate = [s for s in collect_scores(case, n) if s is not None]
    k = key(case.case_id, case.metric.name)
    data = store.load()

    if k not in data:
        update_baseline(store, k, make_record(candidate))
        return Verdict(PASS, None, None, "recorded baseline (cold start)")

    baseline = data[k]["scores"]
    n_valid = min(len(baseline), len(candidate))
    if n_valid < min_valid:
        return decide_gate(1.0, 0.0, n_valid=n_valid, min_valid=min_valid)

    if case.metric.kind == NUMERIC:
        pvalue = numeric_significance(baseline, candidate)
    else:
        pvalue = boolean_significance(baseline, candidate)

    effect = float(np.mean(candidate) - np.mean(baseline))
    if min_effect is None:
        min_effect = DEFAULT_MIN_EFFECT[case.metric.kind]

    return decide_gate(
        pvalue,
        effect,
        polarity=case.metric.polarity,
        alpha=alpha,
        min_effect=min_effect,
        n_valid=n_valid,
        min_valid=min_valid,
        underpowered=is_underpowered(len(baseline), len(candidate), alpha),
    )


def assert_no_regression(case, baseline_path, **kwargs):
    verdict = check_case(case, BaselineStore(baseline_path), **kwargs)
    if verdict.status == FAIL:
        raise AssertionError(f"regression in {case.case_id}: {verdict.reason}")
    return verdict
