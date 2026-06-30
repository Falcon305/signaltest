import os
from typing import Any

from signaltest.report import write_json
from signaltest.results import collector


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--signaltest-json",
        default=None,
        help="write signaltest results to this JSON path",
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
    path = session.config.getoption("signaltest_json", None)
    if path:
        write_json(collector.results, path)
