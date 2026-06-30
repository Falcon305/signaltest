STARTER_TEST = """from signaltest import Case, ExactMatch, assert_no_regression


def test_agent_does_not_regress():
    case = Case(
        case_id="example",
        run=lambda: "4",  # call your agent here, e.g. my_agent("what is 2 + 2?")
        expected="4",
        metric=ExactMatch(),
    )
    assert_no_regression(case, "baselines/example.json", n=10)
"""

STARTER_WORKFLOW = """name: regression
on: pull_request

jobs:
  signaltest:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: Falcon305/signaltest@v0.3.0
        with:
          install: pip install -e ".[dev]"
"""
