from signaltest.stats.gate import Verdict


class ResultCollector:
    def __init__(self) -> None:
        self.results: dict[str, Verdict] = {}

    def record(self, case_id: str, verdict: Verdict) -> None:
        self.results[case_id] = verdict

    def reset(self) -> None:
        self.results = {}


collector = ResultCollector()
