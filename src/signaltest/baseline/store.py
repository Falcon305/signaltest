import json
from pathlib import Path
from typing import Any, Union


class BaselineError(Exception):
    pass


class BaselineStore:
    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text())
        except ValueError as e:
            raise BaselineError(f"baseline file is corrupt: {self.path}") from e

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True))
