# signaltest

[![ci](https://github.com/Falcon305/signaltest/actions/workflows/ci.yml/badge.svg)](https://github.com/Falcon305/signaltest/actions/workflows/ci.yml)

Regression tests for LLM agents that don't fail your CI on noise.

LLMs are non-deterministic, so naive eval checks flake: a score drifts a point on
randomness, CI goes red, the team stops trusting it, and the check gets deleted.
signaltest runs each case several times and blocks a PR only when a regression is
**statistically real and large enough to matter** — then shows a diff of what
actually changed in the agent's run.

Local-first. No account, no service, no data leaves your repo.

Status: early, v0.1 in progress.

## Contents

- [Why](#why)
- [Install](#install)
- [Quick start](#quick-start)
- [Testing a whole suite](#testing-a-whole-suite)
- [Metrics](#metrics)
- [How it works](#how-it-works)
- [Configuration](#configuration)
- [Baselines](#baselines)
- [Using it in CI](#using-it-in-ci)
- [CLI](#cli)
- [Development](#development)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

## Why

Most eval tools score an agent once and compare against a fixed threshold. With a
stochastic model, that threshold flakes: the same prompt scores 0.84 one run and
0.81 the next. CI fails on the bad draw, people stop believing it, and the safety
net is gone.

signaltest treats the score as a distribution, not a number. It samples the agent
`n` times for the candidate, compares against `n` recorded baseline samples, and
only fails when the difference is **statistically significant** *and* clears a
**minimum effect size**. Noise stays green. Real regressions go red.

## Install

```sh
pip install signaltest
```

Or with [uv](https://docs.astral.sh/uv/):

```sh
uv pip install signaltest   # into the active environment
uv add signaltest           # into a uv-managed project
```

## Quick start

Write a normal pytest test. Give signaltest a way to run your agent, the expected
output, and a metric.

```python
from signaltest import Case, assert_no_regression, ExactMatch


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
compare against it and fail the test only on a real regression.

## Testing a whole suite

`run_suite` runs many cases and applies a multiple-comparison correction across
them, so a suite of 50 cases doesn't go red just because one flaked.

```python
from signaltest import Case, run_suite, format_report, exit_code, ExactMatch

cases = [
    Case("math", run=lambda: my_agent("2 + 2?"), expected="4", metric=ExactMatch()),
    Case("geo", run=lambda: my_agent("capital of France?"), expected="Paris", metric=ExactMatch()),
]

results = run_suite(cases, "baselines/agent.json", n=10)
print(format_report(results))
raise SystemExit(exit_code(results))
```

`format_report` prints a per-case summary; `exit_code` returns `1` if any case
regressed, `0` otherwise — drop it straight into a CI step.

A failing case reports the measured effect size and p-value, so you see *how
big* the regression is, not just that one happened:

```
PASS          geo: no significant regression
FAIL          math: significant regression past the effect floor (effect=-0.180, p=0.004)
1 passed, 1 failed, 0 inconclusive
```

## Metrics

A metric declares its `kind` (numeric or boolean, which picks the significance
test) and its `polarity` (is higher or lower better).

| Metric | Kind | Polarity | Scores |
|--------|------|----------|--------|
| `ExactMatch()` | boolean | higher better | `output == expected` |
| `Contains()` | boolean | higher better | `expected in output` |
| `Numeric(name, polarity)` | numeric | configurable | the raw value (latency, cost, judge score) |
| `TrajectoryMatch(ignore_keys=...)` | numeric | higher better | fraction of matching agent tool-calls |

`Numeric` with `polarity="lower_better"` is how you gate latency or cost — a real
*increase* becomes the regression.

```python
from signaltest import Numeric
from signaltest.metrics.base import LOWER_BETTER

latency = Numeric(name="latency_ms", polarity=LOWER_BETTER)
```

`TrajectoryMatch` compares the agent's tool-call path against a reference path and
ignores volatile keys (timestamps, ids):

```python
from signaltest import TrajectoryMatch, Step

expected_path = [Step("search", {"q": "weather"}), Step("answer", {})]
metric = TrajectoryMatch(ignore_keys=("request_id",))
```

## How it works

```
candidate runs n times ─┐
                        ├─> significance test ─┐
stored baseline samples ┘                      ├─> block only if
                                               │   significant AND
                          effect size ─────────┘   past the floor
```

- **Significance** — a permutation test for numeric metrics, Fisher's exact test
  for boolean metrics. Both are seeded, so the same inputs always give the same
  result. The gate that kills flakiness is not itself flaky.
- **Effect floor** — a regression must also clear a minimum effect size, so a
  statistically significant but meaningless 0.1% drift never blocks the build.
- **Multiple comparisons** — across a suite, p-values are adjusted with the
  Benjamini-Hochberg procedure, so flakiness doesn't reappear at the suite level.
- **Power** — cases with too few samples to detect a real change are flagged
  `inconclusive`, never passed silently.
- **Model versioning** — a baseline records the model it was captured under. If you
  pass a new `model=` and it differs, the baseline is re-recorded instead of
  reported as a regression, so a provider model swap can't masquerade as one.

## Configuration

Every `assert_no_regression` / `check_case` / `run_suite` call accepts:

| Argument | Default | Meaning |
|----------|---------|---------|
| `n` | `10` | samples per run (boolean metrics usually want more) |
| `alpha` | `0.05` | significance threshold |
| `min_effect` | `0.03` numeric / `0.10` boolean | minimum effect size to count |
| `min_valid` | `2` | fewer valid samples than this → `inconclusive` |
| `model` | `None` | model id recorded with the baseline |

## Baselines

A baseline is a JSON file committed to your repo. Each entry is keyed by
`case_id::metric_name` and stores the recorded scores and the model.

- **Cold start** — the first run records the baseline and passes.
- **Updating** — to accept a new baseline on purpose, delete the case's entry and
  re-run, or edit the JSON. The change is a reviewable diff in the same PR.
- **Inspecting** — use the CLI (below).

## Using it in CI

Because cases are plain pytest tests, your existing `pytest` step gates them:

```yaml
- run: pip install -e ".[dev]"
- run: pytest
```

A failed case fails the build. Baselines live in the repo, so CI needs no secrets
and nothing leaves your infrastructure.

## CLI

```sh
signaltest version
signaltest baselines baselines/agent.json   # list recorded cases
signaltest show baselines/agent.json math::exact_match
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

With uv the setup is a single command (it creates the environment for you):

```sh
uv sync --extra dev
uv run pytest
```

Try the offline examples (cached responses, no API key):

```sh
python examples/demo.py        # smallest possible case
python examples/tool_agent.py  # tool-using agent: trajectory + answer checks
```

See [docs/architecture.md](docs/architecture.md) for how the pieces fit together
and how to add your own metric.

## FAQ

**Does it call my LLM?** Only through the `run` function you provide. signaltest
never talks to a provider itself.

**How many samples do I need?** `n=10` is a sane default for numeric metrics.
Boolean metrics resolve in coarser steps, so they need more — bump `n` and watch
for `inconclusive`, which means the test can't yet detect a change of the size you
care about.

**Why did a case come back `inconclusive`?** Too few valid samples to be
trustworthy. Increase `n`, or fix whatever made runs error out.

**Does my data leave my machine?** No. Baselines are local JSON; there is no
service.

## Contributing

Issues and pull requests are welcome. Keep changes small and focused, and add a
test for anything you change. See `CONTRIBUTING.md`.

## License

MIT
