import tempfile
from pathlib import Path

from signaltest.metrics.exact import ExactMatch
from signaltest.runner import Case, assert_no_regression

cached = {
    "what is 2 + 2?": "4",
    "capital of france?": "Paris",
}


def agent(question):
    return cached[question]


def main():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "baseline.json"
        case = Case(
            "math",
            run=lambda: agent("what is 2 + 2?"),
            expected="4",
            metric=ExactMatch(),
        )
        first = assert_no_regression(case, path, n=10)
        print("first run:", first.reason)
        second = assert_no_regression(case, path, n=10)
        print("second run:", second.status)


if __name__ == "__main__":
    main()
