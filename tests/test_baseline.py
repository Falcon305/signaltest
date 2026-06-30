import pytest

from signaltest.baseline.store import BaselineError, BaselineStore


def test_missing_file_is_cold_start(tmp_path):
    store = BaselineStore(tmp_path / "baseline.json")
    assert store.load() == {}


def test_save_then_load_roundtrips(tmp_path):
    store = BaselineStore(tmp_path / "baseline.json")
    data = {"case1::exact_match": {"scores": [1, 1, 0], "model": "x"}}
    store.save(data)
    assert store.load() == data


def test_corrupt_file_fails_loud(tmp_path):
    path = tmp_path / "baseline.json"
    path.write_text("{ not valid json")
    with pytest.raises(BaselineError):
        BaselineStore(path).load()


def test_save_creates_parent_dirs(tmp_path):
    store = BaselineStore(tmp_path / "nested" / "dir" / "baseline.json")
    store.save({"a": 1})
    assert store.load() == {"a": 1}


def test_save_is_stable(tmp_path):
    path = tmp_path / "baseline.json"
    store = BaselineStore(path)
    data = {"b": 2, "a": 1}
    store.save(data)
    first = path.read_text()
    store.save(data)
    assert first == path.read_text()
