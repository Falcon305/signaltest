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
    update_baseline(
        BaselineStore(path), key("c1", "exact_match"), make_record([1, 1, 0], model="m1")
    )
    code = main(["baselines", str(path)])
    out = capsys.readouterr().out
    assert "c1::exact_match" in out
    assert "model=m1" in out
    assert code == 0


def test_show_missing_case_returns_1(tmp_path, capsys):
    path = tmp_path / "b.json"
    BaselineStore(path).save({})
    assert main(["show", str(path), "nope"]) == 1


def test_show_prints_record(tmp_path, capsys):
    path = tmp_path / "b.json"
    k = key("c1", "exact_match")
    update_baseline(BaselineStore(path), k, make_record([1, 0, 1], model="m1"))
    code = main(["show", str(path), k])
    out = capsys.readouterr().out
    assert '"model": "m1"' in out
    assert code == 0


def test_no_command_prints_help(capsys):
    code = main([])
    assert "usage" in capsys.readouterr().out.lower()
    assert code == 0


def test_report_renders_markdown(tmp_path, capsys):
    from signaltest.report import write_json
    from signaltest.stats.gate import FAIL, Verdict

    path = tmp_path / "results.json"
    write_json({"math": Verdict(FAIL, pvalue=0.01, effect=-0.2, reason="regression")}, path)
    code = main(["report", str(path)])
    out = capsys.readouterr().out
    assert "<!-- signaltest -->" in out
    assert "❌ fail" in out
    assert code == 0


def test_report_text_format(tmp_path, capsys):
    from signaltest.report import write_json
    from signaltest.stats.gate import PASS, Verdict

    path = tmp_path / "results.json"
    write_json({"geo": Verdict(PASS, None, None, "no significant regression")}, path)
    code = main(["report", str(path), "--format", "text"])
    out = capsys.readouterr().out
    assert "PASS" in out
    assert code == 0


def test_power_recommends_samples(tmp_path, capsys):
    path = tmp_path / "b.json"
    k = key("c1", "numeric")
    update_baseline(BaselineStore(path), k, make_record([1.0, 2.0, 3.0, 4.0], model=None))
    code = main(["power", str(path), k, "--min-effect", "0.5", "--kind", "numeric"])
    out = capsys.readouterr().out
    assert "samples per run" in out
    assert code == 0


def test_power_infers_boolean_kind(tmp_path, capsys):
    path = tmp_path / "b.json"
    k = key("c1", "exact_match")
    update_baseline(BaselineStore(path), k, make_record([True, False, True, True], model=None))
    code = main(["power", str(path), k, "--min-effect", "0.1"])
    out = capsys.readouterr().out
    assert "samples per run" in out
    assert code == 0


def test_power_infers_numeric_kind(tmp_path, capsys):
    path = tmp_path / "b.json"
    k = key("c1", "numeric")
    update_baseline(BaselineStore(path), k, make_record([1.5, 2.7, 3.1, 4.9], model=None))
    code = main(["power", str(path), k, "--min-effect", "0.5"])
    out = capsys.readouterr().out
    assert "samples per run" in out
    assert code == 0


def test_power_missing_case_returns_1(tmp_path, capsys):
    path = tmp_path / "b.json"
    BaselineStore(path).save({})
    assert main(["power", str(path), "nope", "--min-effect", "0.1"]) == 1


def test_rm_deletes_entry(tmp_path, capsys):
    path = tmp_path / "b.json"
    k = key("c1", "exact_match")
    update_baseline(BaselineStore(path), k, make_record([1, 0, 1], model=None))
    code = main(["rm", str(path), k])
    assert code == 0
    assert k not in BaselineStore(path).load()


def test_rm_missing_case_returns_1(tmp_path, capsys):
    path = tmp_path / "b.json"
    BaselineStore(path).save({})
    assert main(["rm", str(path), "nope"]) == 1
