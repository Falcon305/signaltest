from signaltest.baseline.record import key, make_record, update_baseline
from signaltest.baseline.store import BaselineStore


def test_update_records_into_empty_store(tmp_path):
    store = BaselineStore(tmp_path / "b.json")
    update_baseline(store, key("c1", "exact_match"), make_record([1, 1, 0], model="m"))
    record = store.load()["c1::exact_match"]
    assert record["scores"] == [1, 1, 0]
    assert record["model"] == "m"


def test_update_overwrites_existing_key(tmp_path):
    store = BaselineStore(tmp_path / "b.json")
    k = key("c1", "exact_match")
    update_baseline(store, k, make_record([0, 0]))
    update_baseline(store, k, make_record([1, 1]))
    assert store.load()[k]["scores"] == [1, 1]


def test_update_preserves_other_keys(tmp_path):
    store = BaselineStore(tmp_path / "b.json")
    update_baseline(store, key("c1", "m"), make_record([1]))
    update_baseline(store, key("c2", "m"), make_record([0]))
    assert set(store.load()) == {"c1::m", "c2::m"}
