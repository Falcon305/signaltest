from typing import Any


def pytest_configure(config: Any) -> None:
    config.addinivalue_line("markers", "signaltest: mark a regression case for signaltest")
