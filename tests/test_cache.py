from signaltest.baseline.cache import ScoreCache
from signaltest.baseline.store import BaselineStore
from signaltest.metrics.exact import ExactMatch
from signaltest.runner import Case, check_case, collect_scores


def test_cache_get_put_roundtrip(tmp_path):
    cache = ScoreCache(tmp_path / "c.json")
    assert cache.get("k") is None
    cache.put("k", [1, 0, 1])
    assert cache.get("k") == [1, 0, 1]


def test_collect_scores_reuses_cache(tmp_path):
    calls = {"n": 0}

    def run():
        calls["n"] += 1
        return "4"

    case = Case("c", run=run, expected="4", metric=ExactMatch(), cache_key="v1")
    cache = ScoreCache(tmp_path / "c.json")
    first = collect_scores(case, 5, cache)
    after_first = calls["n"]
    second = collect_scores(case, 5, cache)
    assert after_first == 5
    assert calls["n"] == 5  # second call served from cache, no extra runs
    assert first == second


def test_collect_scores_without_cache_key_always_runs(tmp_path):
    calls = {"n": 0}

    def run():
        calls["n"] += 1
        return "4"

    case = Case("c", run=run, expected="4", metric=ExactMatch())
    cache = ScoreCache(tmp_path / "c.json")
    collect_scores(case, 3, cache)
    collect_scores(case, 3, cache)
    assert calls["n"] == 6


def test_check_case_threads_cache(tmp_path):
    calls = {"n": 0}

    def run():
        calls["n"] += 1
        return "4"

    case = Case("c", run=run, expected="4", metric=ExactMatch(), cache_key="v1")
    store = BaselineStore(tmp_path / "b.json")
    cache_path = tmp_path / "cache.json"
    check_case(case, store, n=6, cache=cache_path)
    runs_after_record = calls["n"]
    check_case(case, store, n=6, cache=cache_path)
    assert calls["n"] == runs_after_record
