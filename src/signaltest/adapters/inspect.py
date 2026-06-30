from typing import Any

# Inspect AI records correct/incorrect scores as letter grades on some scorers.
_GRADES = {"C": 1.0, "I": 0.0, "P": 1.0, "N": 0.0}


def scores_from_inspect_log(log: Any, scorer: str) -> list[float]:
    """Pull a scorer's per-sample values out of an Inspect AI eval log.

    Works on the parsed log (a dict from JSON, or an `EvalLog` object): each
    sample contributes one value, so epochs become repeated samples — exactly
    what `compare_scores` wants.
    """
    samples = log["samples"] if isinstance(log, dict) else log.samples
    values = []
    for sample in samples:
        scores = sample["scores"] if isinstance(sample, dict) else sample.scores
        entry = scores[scorer]
        value = entry["value"] if isinstance(entry, dict) else entry.value
        values.append(_coerce(value))
    return values


def _coerce(value: Any) -> float:
    if isinstance(value, str):
        grade = _GRADES.get(value.upper())
        if grade is not None:
            return grade
    return float(value)
