import pytest

from signaltest import config as cfg
from signaltest.baseline.store import BaselineStore
from signaltest.metrics.numeric import Numeric
from signaltest.runner import Case, check_case


@pytest.fixture(autouse=True)
def _reset_config():
    yield
    cfg.reset_config()


def test_defaults_are_present():
    assert cfg.get("n") == 10
    assert cfg.get("alpha") == 0.05
    assert cfg.get("test") == "permutation"


def test_configure_overrides_known_keys_only():
    cfg.configure(n=25, unknown="ignored")
    assert cfg.get("n") == 25
    assert "unknown" not in cfg._CONFIG


def test_reset_restores_defaults():
    cfg.configure(alpha=0.2)
    cfg.reset_config()
    assert cfg.get("alpha") == 0.05


def test_load_pyproject_reads_section(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        "[tool.signaltest]\nn = 30\nalpha = 0.01\n", encoding="utf-8"
    )
    section = cfg.load_pyproject(tmp_path / "pyproject.toml")
    assert section == {"n": 30, "alpha": 0.01}


def test_load_pyproject_missing_file(tmp_path):
    assert cfg.load_pyproject(tmp_path / "nope.toml") == {}


def test_configured_n_is_used_by_check_case(tmp_path):
    calls = {"n": 0}

    def run():
        calls["n"] += 1
        return 0.8

    cfg.configure(n=7)
    case = Case("c", run=run, expected=None, metric=Numeric("q"))
    check_case(case, BaselineStore(tmp_path / "b.json"))  # no explicit n
    assert calls["n"] == 7


def test_explicit_argument_beats_config(tmp_path):
    calls = {"n": 0}

    def run():
        calls["n"] += 1
        return 0.8

    cfg.configure(n=7)
    case = Case("c", run=run, expected=None, metric=Numeric("q"))
    check_case(case, BaselineStore(tmp_path / "b.json"), n=3)
    assert calls["n"] == 3
