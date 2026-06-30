from signaltest import __version__
from signaltest.baseline.record import key, make_record, update_baseline
from signaltest.baseline.store import BaselineStore
from signaltest.cli import main


def test_version_command(capsys):
    code = main(["version"])
    assert __version__ in capsys.readouterr().out
    assert code == 0


def test_baselines_lists_cases(tmp_path, capsys):
    path = tmp_path / "b.json"
    update_baseline(BaselineStore(path), key("c1", "exact_match"), make_record([1, 1, 0], model="m1"))
    code = main(["baselines", str(path)])
    out = capsys.readouterr().out
    assert "c1::exact_match" in out
    assert "model=m1" in out
    assert code == 0


def test_show_missing_case_returns_1(tmp_path, capsys):
    path = tmp_path / "b.json"
    BaselineStore(path).save({})
    assert main(["show", str(path), "nope"]) == 1
