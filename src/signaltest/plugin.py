import os
from datetime import datetime
from typing import Any

from signaltest.history import append_history
from signaltest.report import write_json
from signaltest.results import collector


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--signaltest-json",
        default=None,
        help="write signaltest results to this JSON path",
    )
    parser.addoption(
        "--signaltest-history",
        default=None,
        help="append this run's verdicts to a history JSONL file",
    )
    parser.addoption(
        "--signaltest-update",
        action="store_true",
        default=False,
        help="re-record baselines instead of comparing against them",
    )


def pytest_configure(config: Any) -> None:
    config.addinivalue_line("markers", "signaltest: mark a regression case for signaltest")
    if config.getoption("signaltest_update", False):
        os.environ["SIGNALTEST_UPDATE"] = "1"


def pytest_sessionstart(session: Any) -> None:
    collector.reset()


def pytest_sessionfinish(session: Any, exitstatus: Any) -> None:
    json_path = session.config.getoption("signaltest_json", None)
    if json_path:
        write_json(collector.results, json_path)
    history_path = session.config.getoption("signaltest_history", None)
    if history_path:
        append_history(
            collector.results, history_path, datetime.now().isoformat(timespec="seconds")
        )
