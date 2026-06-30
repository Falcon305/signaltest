from signaltest.adapters import scores_from_deepeval, scores_from_inspect_log
from signaltest.compare import compare_scores
from signaltest.metrics.base import Metric
from signaltest.metrics.contains import Contains
from signaltest.metrics.exact import ExactMatch
from signaltest.metrics.judge import LLMJudge
from signaltest.metrics.numeric import Numeric
from signaltest.metrics.rag import AnswerRelevancy, Faithfulness
from signaltest.metrics.trajectory import TrajectoryMatch
from signaltest.report import (
    describe,
    exit_code,
    format_report,
    read_json,
    to_html,
    to_markdown,
    write_json,
)
from signaltest.runner import Case, assert_no_regression, check_case, run_suite
from signaltest.stats.gate import FAIL, INCONCLUSIVE, PASS
from signaltest.trajectory.diff import render_diff
from signaltest.trajectory.model import Step

__version__ = "0.2.0"

__all__ = [
    "Case",
    "assert_no_regression",
    "check_case",
    "run_suite",
    "compare_scores",
    "scores_from_inspect_log",
    "scores_from_deepeval",
    "format_report",
    "to_markdown",
    "to_html",
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
    "Faithfulness",
    "AnswerRelevancy",
    "Step",
    "PASS",
    "FAIL",
    "INCONCLUSIVE",
    "__version__",
]
