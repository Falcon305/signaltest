"""signaltest as a CI gate over a real agent — the full loop.

Step 1, record the baseline on the good prompt:

    export ANTHROPIC_API_KEY=sk-...
    pytest examples/real_agent/test_quality.py

Step 2, ship a "bad" prompt change and watch the gate go red:

    SIGNALTEST_PROMPT=regressed pytest examples/real_agent/test_quality.py -s

Delete examples/real_agent/baselines/qa.json to start over. Sequential sampling
keeps the cost down: unchanged questions settle in a few calls.
"""

import os

import pytest
from agent import GOOD_PROMPT, QUESTIONS, REGRESSED_PROMPT, ConciseAnswer, ask

from signaltest import Case, run_suite
from signaltest.report import format_report

BASELINE = os.path.join(os.path.dirname(__file__), "baselines", "qa.json")

pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="set ANTHROPIC_API_KEY to run the real-agent demo",
)


def _active_prompt() -> str:
    if os.environ.get("SIGNALTEST_PROMPT") == "regressed":
        return REGRESSED_PROMPT
    return GOOD_PROMPT


def test_agent_quality() -> None:
    prompt = _active_prompt()
    cases = [
        Case(
            f"q{i}", run=lambda q=question: ask(q, prompt), expected=answer, metric=ConciseAnswer()
        )
        for i, (question, answer) in enumerate(QUESTIONS)
    ]
    results = run_suite(cases, BASELINE, n=4, max_n=12, sequential=True)
    print("\n" + format_report(results))
    failed = [case_id for case_id, verdict in results.items() if verdict.status == "fail"]
    assert not failed, f"regressions detected: {failed}"
