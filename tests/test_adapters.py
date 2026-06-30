from dataclasses import dataclass

from signaltest.adapters import scores_from_deepeval, scores_from_inspect_log
from signaltest.compare import compare_scores
from signaltest.metrics.base import NUMERIC
from signaltest.stats.gate import FAIL


def test_inspect_log_numeric_values():
    log = {
        "samples": [
            {"scores": {"accuracy": {"value": 0.9}}},
            {"scores": {"accuracy": {"value": 0.8}}},
        ]
    }
    assert scores_from_inspect_log(log, "accuracy") == [0.9, 0.8]


def test_inspect_log_letter_grades():
    log = {
        "samples": [
            {"scores": {"match": {"value": "C"}}},
            {"scores": {"match": {"value": "I"}}},
        ]
    }
    assert scores_from_inspect_log(log, "match") == [1.0, 0.0]


def test_inspect_log_object_shape():
    @dataclass
    class Entry:
        value: float

    @dataclass
    class Sample:
        scores: dict

    @dataclass
    class Log:
        samples: list

    log = Log(samples=[Sample({"acc": Entry(0.7)}), Sample({"acc": Entry(0.6)})])
    assert scores_from_inspect_log(log, "acc") == [0.7, 0.6]


def test_deepeval_pulls_named_metric():
    results = [
        {"metrics_data": [{"name": "relevancy", "score": 0.9}, {"name": "bias", "score": 0.1}]},
        {"metrics_data": [{"name": "relevancy", "score": 0.85}]},
    ]
    assert scores_from_deepeval(results, "relevancy") == [0.9, 0.85]


def test_deepeval_object_shape():
    @dataclass
    class MetricData:
        name: str
        score: float

    @dataclass
    class Result:
        metrics_data: list

    results = [Result([MetricData("faith", 0.5)]), Result([MetricData("faith", 0.4)])]
    assert scores_from_deepeval(results, "faith") == [0.5, 0.4]


def test_adapter_output_feeds_compare_scores():
    base = {"samples": [{"scores": {"a": {"value": 0.9}}} for _ in range(12)]}
    cand = {"samples": [{"scores": {"a": {"value": 0.5}}} for _ in range(12)]}
    verdict = compare_scores(
        scores_from_inspect_log(base, "a"),
        scores_from_inspect_log(cand, "a"),
        kind=NUMERIC,
    )
    assert verdict.status == FAIL
