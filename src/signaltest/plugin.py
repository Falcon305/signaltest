def pytest_configure(config):
    config.addinivalue_line("markers", "signaltest: mark a regression case for signaltest")
