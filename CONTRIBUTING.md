# Contributing

Thanks for your interest in signaltest.

## Setup

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pre-commit install   # optional: run the linters on every commit
```

## Before opening a PR

- Add a test for anything you change.
- Run the checks (the same ones CI runs):

```sh
ruff check src tests examples
ruff format --check src tests examples
mypy
coverage run -m pytest && coverage report
```

- Keep changes small and focused — one idea per PR.
- Match the existing style: simple, direct code, few comments.

## Reporting bugs

Open an issue with a minimal reproduction: the metric, the inputs, and what you
expected versus what happened.
