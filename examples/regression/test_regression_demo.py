"""A self-contained regression suite used to demo the GitHub Action.

The agents are deterministic and offline, so the result is reproducible: one
case passes, one regresses (a real drop past the effect floor), one boolean
case passes. The PR comment shows each with its effect size and 95% CI bar.
"""

from signaltest import Case, ExactMatch, Numeric, exit_code, format_report, run_suite

GOOD = [0.82, 0.79, 0.81, 0.80, 0.83, 0.78, 0.81, 0.80, 0.82, 0.79, 0.81, 0.80]
REGRESSED = [0.62, 0.59, 0.61, 0.60, 0.63, 0.58, 0.61, 0.60, 0.62, 0.59, 0.61, 0.60]

BASELINE = "examples/regression/baselines/demo.json"


def sequence_agent(values):
    state = {"i": 0}

    def run():
        value = values[state["i"] % len(values)]
        state["i"] += 1
        return value

    return run


def test_regression_demo():
    cases = [
        Case("answer_quality", run=sequence_agent(GOOD), expected=None, metric=Numeric("quality")),
        Case(
            "answer_quality_v2",
            run=sequence_agent(REGRESSED),
            expected=None,
            metric=Numeric("quality"),
        ),
        Case("exact_answer", run=lambda: "Paris", expected="Paris", metric=ExactMatch()),
    ]
    results = run_suite(cases, BASELINE, n=12)
    print(format_report(results))
    assert exit_code(results) == 0
