from typing import Any

from signaltest.report import write_json
from signaltest.results import collector


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--signaltest-json",
        default=None,
        help="write signaltest results to this JSON path",
    )


def pytest_configure(config: Any) -> None:
    config.addinivalue_line("markers", "signaltest: mark a regression case for signaltest")


def pytest_sessionstart(session: Any) -> None:
    collector.reset()


def pytest_sessionfinish(session: Any, exitstatus: Any) -> None:
    path = session.config.getoption("signaltest_json", None)
    if path:
        write_json(collector.results, path)
