import os

from signaltest import plugin
from signaltest.report import read_json
from signaltest.results import collector
from signaltest.runner import Case
from signaltest.stats.gate import PASS, Verdict


def test_case_holds_fields():
    c = Case("c1", run=lambda: "x", expected="x", metric=None)
    assert c.case_id == "c1"
    assert c.run() == "x"
    assert c.expected == "x"


def test_plugin_registers_marker():
    recorded = []

    class FakeConfig:
        def addinivalue_line(self, name, value):
            recorded.append((name, value))

        def getoption(self, name, default=None):
            return False

    plugin.pytest_configure(FakeConfig())
    assert any("signaltest" in value for _, value in recorded)


def test_configure_sets_update_env(monkeypatch):
    monkeypatch.setenv("SIGNALTEST_UPDATE", "0")

    class FakeConfig:
        def addinivalue_line(self, name, value):
            pass

        def getoption(self, name, default=None):
            return True

    plugin.pytest_configure(FakeConfig())
    assert os.environ["SIGNALTEST_UPDATE"] == "1"


class _Parser:
    def __init__(self):
        self.options = {}

    def addoption(self, name, **kwargs):
        self.options[name] = kwargs


class _Session:
    def __init__(self, **options):
        self.config = _Config(**options)


class _Config:
    def __init__(self, **options):
        self._options = options

    def getoption(self, name, default=None):
        return self._options.get(name, default)


def test_addoption_registers_flags():
    parser = _Parser()
    plugin.pytest_addoption(parser)
    assert "--signaltest-json" in parser.options
    assert "--signaltest-update" in parser.options


def test_sessionstart_resets_collector():
    collector.record("stale", Verdict(PASS, None, None, "old"))
    plugin.pytest_sessionstart(_Session())
    assert collector.results == {}


def test_sessionfinish_writes_json_when_path_set(tmp_path):
    collector.reset()
    collector.record("c", Verdict(PASS, None, None, "ok"))
    path = tmp_path / "out.json"
    plugin.pytest_sessionfinish(_Session(signaltest_json=str(path)), 0)
    assert "c" in read_json(path)


def test_sessionfinish_appends_history_when_path_set(tmp_path):
    from signaltest.history import read_history

    collector.reset()
    collector.record("c", Verdict(PASS, None, None, "ok"))
    path = tmp_path / "hist.jsonl"
    plugin.pytest_sessionfinish(_Session(signaltest_history=str(path)), 0)
    runs = read_history(path)
    assert len(runs) == 1
    assert "c" in runs[0]["cases"]


def test_sessionfinish_noop_without_path():
    collector.reset()
    plugin.pytest_sessionfinish(_Session(), 0)
