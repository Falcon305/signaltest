from collections.abc import Sequence
from typing import Any, Optional

from signaltest.baseline.store import BaselineStore

Record = dict[str, Any]


def key(case_id: str, metric_name: str) -> str:
    return f"{case_id}::{metric_name}"


def make_record(scores: Sequence[Any], model: Optional[str] = None) -> Record:
    return {"scores": list(scores), "model": model}


def update_baseline(store: BaselineStore, key: str, record: Record) -> dict[str, Record]:
    data = store.load()
    data[key] = record
    store.save(data)
    return data
