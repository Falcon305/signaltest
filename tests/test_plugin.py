from signaltest import plugin
from signaltest.runner import Case


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

    plugin.pytest_configure(FakeConfig())
    assert any("signaltest" in value for _, value in recorded)
