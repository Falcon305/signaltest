import threading

from signaltest.metrics.exact import ExactMatch
from signaltest.runner import Case, collect_scores


def test_parallel_collects_all_samples():
    lock = threading.Lock()
    calls = {"n": 0}

    def run():
        with lock:
            calls["n"] += 1
        return "4"

    case = Case("c", run=run, expected="4", metric=ExactMatch())
    scores = collect_scores(case, 8, workers=4)
    assert len(scores) == 8
    assert calls["n"] == 8
    assert all(s is True for s in scores)


def test_parallel_matches_serial():
    def make():
        return Case("c", run=lambda: "4", expected="4", metric=ExactMatch())

    serial = collect_scores(make(), 6, workers=1)
    parallel = collect_scores(make(), 6, workers=3)
    assert serial == parallel
