from signaltest.metrics.base import Metric
from signaltest.metrics.contains import Contains
from signaltest.metrics.exact import ExactMatch
from signaltest.metrics.judge import LLMJudge
from signaltest.metrics.numeric import Numeric
from signaltest.metrics.trajectory import TrajectoryMatch
from signaltest.report import (
    describe,
    exit_code,
    format_report,
    read_json,
    to_markdown,
    write_json,
)
from signaltest.runner import Case, assert_no_regression, check_case, run_suite
from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS
from signaltest.trajectory.diff import render_diff
from signaltest.trajectory.model import Step

__version__ = "0.1.0"

__all__ = [
    "Case",
    "assert_no_regression",
    "check_case",
    "run_suite",
    "format_report",
    "to_markdown",
    "write_json",
    "read_json",
    "describe",
    "exit_code",
    "render_diff",
    "Metric",
    "ExactMatch",
    "Contains",
    "Numeric",
    "TrajectoryMatch",
    "LLMJudge",
    "Step",
    "PASS",
    "FAIL",
    "INCONCLUSIVE",
    "__version__",
]
