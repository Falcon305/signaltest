from typing import Any


def scores_from_deepeval(test_results: Any, metric: str) -> list[float]:
    """Pull a metric's score from each DeepEval test result.

    Accepts the parsed results (dicts or objects). Run your DeepEval suite once
    for the baseline and once for the candidate, then hand both arrays to
    `compare_scores`.
    """
    values = []
    for result in test_results:
        metrics = result["metrics_data"] if isinstance(result, dict) else result.metrics_data
        for data in metrics:
            name = data["name"] if isinstance(data, dict) else data.name
            if name == metric:
                score = data["score"] if isinstance(data, dict) else data.score
                values.append(float(score))
                break
    return values
