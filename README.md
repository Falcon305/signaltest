# signaltest

Regression tests for LLM agents that don't fail your CI on noise.

LLMs are non-deterministic, so naive eval checks flake: a score drifts a point on
randomness, CI goes red, and the team stops trusting it. signaltest runs each case
several times and blocks a PR only when a regression is statistically real, not
noise — then shows a diff of what actually changed in the agent's run.

Local-first. No account, no data leaves your repo.

Status: early, v0.1 in progress.

## Install

```sh
pip install signaltest
```

## Quick start

Write a normal pytest test. Give signaltest a way to run your agent, the expected
output, and a metric. It samples the agent `n` times, compares against a stored
baseline, and fails only on a statistically real regression.

```python
from signaltest.runner import Case, assert_no_regression
from signaltest.metrics.exact import ExactMatch


def test_math_agent():
    case = Case(
        case_id="math_qa",
        run=lambda: my_agent("what is 2 + 2?"),
        expected="4",
        metric=ExactMatch(),
    )
    assert_no_regression(case, "baselines/math_agent.json", n=10)
```

The first run records a baseline (committed as JSON in your repo). Later runs
compare against it. To accept a new baseline on purpose, delete the case's entry
and re-run, or update the JSON — the change shows up as a reviewable diff.

## How it works

```
candidate runs n times ─┐
                        ├─> significance test ─┐
stored baseline samples ┘                      ├─> block only if
                                               │   significant AND
                          effect size ─────────┘   past the floor
```

- Significance: permutation test for numeric metrics, Fisher's exact for boolean.
- A regression must clear both a significance threshold and a minimum effect size,
  so a tiny meaningless drift never blocks the build.
- Underpowered cases (too few samples to detect a real change) are flagged, never
  passed silently.

## Try the demo

Runs fully offline with cached responses, no API key:

```sh
python examples/demo.py
```

## Development

```sh
git clone https://github.com/Falcon305/signaltest
cd signaltest
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests examples
```

## Contributing

Issues and pull requests are welcome. Keep changes small and focused, and add a
test for anything you change.

## License

MIT
