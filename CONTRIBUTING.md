# Contributing

Thanks for your interest in signaltest.

## Setup

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
```

## Before opening a PR

- Add a test for anything you change.
- Run the suite and the linter:

```sh
pytest
ruff check src tests examples
```

- Keep changes small and focused — one idea per PR.
- Match the existing style: simple, direct code, few comments.

## Reporting bugs

Open an issue with a minimal reproduction: the metric, the inputs, and what you
expected versus what happened.
