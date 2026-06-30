"""A tool-using agent tested with signaltest, fully offline.

The agent answers questions by calling a search tool and then composing an
answer. We gate two things per question: that it takes the right tool path
(TrajectoryMatch) and that the answer is correct (Contains). Responses are
cached so the example runs without any API key.
"""

import tempfile
from pathlib import Path

from signaltest import (
    Case,
    Contains,
    Step,
    TrajectoryMatch,
    exit_code,
    format_report,
    run_suite,
)

KNOWLEDGE = {
    "weather in paris": ("sunny, 21C", "search"),
    "capital of japan": ("Tokyo", "lookup"),
}


def agent(question):
    """Returns (answer, trajectory) — what the agent said and how it got there."""
    answer, tool = KNOWLEDGE[question]
    trajectory = [Step(tool, {"q": question}), Step("answer", {})]
    return answer, trajectory


def answer_case(question, expected):
    return Case(
        case_id=f"{question}::answer",
        run=lambda: agent(question)[0],
        expected=expected,
        metric=Contains(),
    )


def path_case(question, expected_path):
    return Case(
        case_id=f"{question}::path",
        run=lambda: agent(question)[1],
        expected=expected_path,
        metric=TrajectoryMatch(ignore_keys=("q",)),
    )


def main():
    cases = [
        answer_case("weather in paris", "21C"),
        path_case("weather in paris", [Step("search", {}), Step("answer", {})]),
        answer_case("capital of japan", "Tokyo"),
        path_case("capital of japan", [Step("lookup", {}), Step("answer", {})]),
    ]

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "baseline.json"
        run_suite(cases, path, n=8)  # cold start records the baseline
        results = run_suite(cases, path, n=8)  # compares against it
        print(format_report(results))
        return exit_code(results)


if __name__ == "__main__":
    raise SystemExit(main())
