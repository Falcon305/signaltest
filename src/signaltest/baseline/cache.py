import json
from pathlib import Path
from typing import Any, Optional, Union


class ScoreCache:
    """Reuse sampled scores across runs, keyed by the case's `cache_key`."""

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        data: dict[str, Any] = json.loads(self.path.read_text())
        return data

    def get(self, key: str) -> Optional[list[Any]]:
        value: Optional[list[Any]] = self._load().get(key)
        return value

    def put(self, key: str, scores: list[Any]) -> None:
        data = self._load()
        data[key] = list(scores)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True))
