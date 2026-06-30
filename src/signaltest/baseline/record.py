def key(case_id, metric_name):
    return f"{case_id}::{metric_name}"


def make_record(scores, model=None):
    return {"scores": list(scores), "model": model}


def update_baseline(store, key, record):
    data = store.load()
    data[key] = record
    store.save(data)
    return data
