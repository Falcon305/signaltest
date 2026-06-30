import sys
from pathlib import Path
from typing import Any, Union

if sys.version_info >= (3, 11):  # pragma: no cover
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

_DEFAULTS: dict[str, Any] = {
    "n": 10,
    "alpha": 0.05,
    "min_effect": None,
    "min_valid": 2,
    "workers": 1,
    "test": "permutation",
    "sequential": False,
    "max_n": None,
    "looks": 4,
    "spending": "obrien_fleming",
}

_CONFIG: dict[str, Any] = dict(_DEFAULTS)


def get(name: str) -> Any:
    return _CONFIG[name]


def configure(**values: Any) -> None:
    for key, value in values.items():
        if key in _CONFIG:
            _CONFIG[key] = value


def reset_config() -> None:
    _CONFIG.clear()
    _CONFIG.update(_DEFAULTS)


def load_pyproject(path: Union[str, Path] = "pyproject.toml") -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {}
    data = tomllib.loads(target.read_text())
    section: dict[str, Any] = data.get("tool", {}).get("signaltest", {})
    return section
