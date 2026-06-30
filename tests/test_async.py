import asyncio

from signaltest.baseline.store import BaselineStore
from signaltest.metrics.exact import ExactMatch
from signaltest.runner import Case, check_case, collect_scores


def test_async_run_is_awaited():
    async def agent():
        await asyncio.sleep(0)
        return "4"

    case = Case("c", run=agent, expected="4", metric=ExactMatch())
    scores = collect_scores(case, 5)
    assert all(s is True for s in scores)


def test_async_run_with_workers():
    async def agent():
        await asyncio.sleep(0)
        return "4"

    case = Case("c", run=agent, expected="4", metric=ExactMatch())
    scores = collect_scores(case, 6, workers=3)
    assert scores == [True] * 6


def test_async_case_records_baseline(tmp_path):
    async def agent():
        return "4"

    case = Case("c", run=agent, expected="4", metric=ExactMatch())
    store = BaselineStore(tmp_path / "b.json")
    verdict = check_case(case, store, n=6)
    assert verdict.status == "pass"
