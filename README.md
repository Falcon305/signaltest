# signaltest

[![ci](https://github.com/Falcon305/signaltest/actions/workflows/ci.yml/badge.svg)](https://github.com/Falcon305/signaltest/actions/workflows/ci.yml)

Regression tests for LLM agents that don't fail your CI on noise.

LLMs are non-deterministic, so naive eval checks flake: a score drifts a point on
randomness, CI goes red, the team stops trusting it, and the check gets deleted.
signaltest runs each case several times and blocks a PR only when a regression is
**statistically real and large enough to matter** — then shows a diff of what
actually changed in the agent's run.

Local-first. No account, no service, no data leaves your repo.

Status: v0.7.0.

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

The difference, on three scenarios (run it yourself with `python examples/flaky.py`):

```
scenario                   naive threshold  signaltest
--------------------------------------------------------
pure noise (same model)    FAIL             PASS
trivial 0.5% drift         FAIL             PASS
real 15% regression        FAIL             FAIL
```

A "did the mean drop?" threshold fails CI on noise and on meaningless drift.
signaltest stays green until a regression is real *and* large enough to matter.

This holds up under a Monte Carlo ([benchmark/](benchmark/)): on pure noise a
"did the mean drop?" gate fails ~50% of runs, and a fixed 2% margin degrades from
1% to 25% false alarms as the metric gets noisier — while signaltest holds its
false-alarm rate near the 5% it was asked for, at every noise level, without
retuning.

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

Run `signaltest init` to drop a starter test in `tests/`, or write one yourself.
Give signaltest a way to run your agent, the expected output, and a metric.

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
| `LLMJudge(judge)` | numeric | higher better | your `judge(output, expected) -> float` |
| `Faithfulness(judge)` | numeric | higher better | grounding of an answer in its context |
| `AnswerRelevancy(judge)` | numeric | higher better | relevance of an answer to the question |

The judge metrics wrap a scoring callable you supply, so no LLM provider is baked
in — point them at any model (or a deterministic stub in tests).

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

- **Significance** — a permutation test for numeric metrics (or Mann-Whitney via
  `test="mannwhitney"`), Fisher's exact test for boolean metrics. The numeric
  tests are seeded, so the same inputs always give the same result. The gate that
  kills flakiness is not itself flaky.
- **Effect floor** — a regression must also clear a minimum effect size, so a
  statistically significant but meaningless 0.1% drift never blocks the build.
- **Confidence interval** — every measured case carries a bootstrap 95% interval
  for the effect, reported as numbers and as a bar that shows at a glance whether
  the interval excludes zero:

  ```
  regression   ━━━━━━━━━·│··········   (interval sits left of zero)
  noise        ··━━━━━━━━╋━━━━━━━━━━   (interval straddles zero)
  ```
- **Multiple comparisons** — across a suite, p-values are adjusted with the
  Benjamini-Hochberg procedure, so flakiness doesn't reappear at the suite level.
  A sequential suite instead spends alpha across both the looks and the cases, so
  the suite-wide false-positive rate stays bounded even with early stopping.
- **Power** — cases with too few samples to detect a real change are flagged
  `inconclusive`, never passed silently.
- **Sequential stopping** (opt-in) — samples in batches and stops as soon as the
  verdict is clear, spending alpha across the looks so peeking stays honest.
- **Paired comparison** (opt-in) — when scores are matched per input, a
  signed-rank test removes between-input variance and needs far fewer samples.
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
| `cache` | `None` | path to reuse sampled scores (see below) |
| `workers` | `1` | sample concurrently with this many threads |
| `test` | `"permutation"` | numeric significance test (`"mannwhitney"` for the rank-based alternative) |
| `sequential` | `False` | draw samples in batches and stop once the gate is conclusive |
| `max_n` | `3 × n` | sample cap when `sequential=True` (`n` becomes the minimum) |
| `looks` | `4` | number of interim checks spread from `n` to `max_n` |
| `spending` | `"obrien_fleming"` | how alpha is split across looks (`"pocock"` spends it evenly) |

Set project-wide defaults once in `pyproject.toml` instead of passing them on
every call (an explicit argument always wins):

```toml
[tool.signaltest]
n = 20
alpha = 0.01
test = "mannwhitney"
```

When a case comes back `inconclusive`, the reason tells you roughly how many
samples it would take to detect the effect you set — e.g.
`underpowered, increase samples (try ~24)`.

### Caching expensive runs

Sampling `n` times is the cost of the method. If your agent is expensive, give a
case a `cache_key` (bump it whenever the prompt or model changes) and pass a
`cache` path. Identical keys reuse the stored scores instead of calling the agent
again:

```python
case = Case("math", run=my_agent, expected="4", metric=ExactMatch(), cache_key="v1")
assert_no_regression(case, "baselines/math.json", cache=".signaltest-cache.json")
```

For agents that are slow rather than costly, pass `workers=N` to sample the `n`
runs concurrently.

### Sequential testing

Most cases haven't changed, so spending a full `n` calls on every one is wasteful.
With `sequential=True`, signaltest samples in batches and stops as soon as the
verdict is clear — an obviously-fine case settles in a few runs, and only the
borderline ones spend the full budget (up to `max_n`):

```python
assert_no_regression(case, "baselines/math.json", n=5, max_n=30, sequential=True)
```

It stays rigorous: alpha is spent across the interim looks (so peeking can't
inflate false positives) using an O'Brien-Fleming schedule by default — almost
none early, most at the final look — so an early stop demands strong evidence
while the final decision keeps nearly full power (`spending="pocock"` spreads it
evenly). A `pass` is reached early only once the effect's confidence interval
sits within the no-meaningful-regression threshold. Each
verdict reports how many runs it actually took, and `workers=N` samples each
look's batch concurrently for slow agents. In a `run_suite`, alpha is also
spent across the cases, so a sequential suite keeps its suite-wide false-positive
rate bounded — the multiplicity protection that Benjamini-Hochberg gives the
fixed-sample path.

## Baselines

A baseline is a JSON file committed to your repo. Each entry is keyed by
`case_id::metric_name` and stores the recorded scores and the model.

- **Cold start** — the first run records the baseline and passes.
- **Updating** — accept new baselines the way you would update snapshots: run
  `pytest --signaltest-update` (or pass `update=True`) to re-record every case, or
  drop one entry with `signaltest rm <path> <case>`. The change is a reviewable
  diff in the same PR.
- **Inspecting** — use the CLI (below).

## Using it in CI

Because cases are plain pytest tests, your existing `pytest` step gates them:

```yaml
- run: pip install -e ".[dev]"
- run: pytest
```

A failed case fails the build. Baselines live in the repo, so CI needs no secrets
and nothing leaves your infrastructure.

### GitHub Action with PR comments

The bundled action runs your cases and posts a sticky results table on the pull
request — updated in place on every push, so reviewers see the effect size and
p-value of any regression next to the diff. Here is one on a real PR
([live example](https://github.com/Falcon305/signaltest/pull/1)):

| Case | Status | Detail | 95% CI |
| --- | --- | --- | --- |
| answer_quality | ✅ pass | no significant regression (effect=+0.000, 95% CI [-0.011, +0.011], p=1.000) | `━━━━━━━━━━╋━━━━━━━━━━` |
| answer_quality_v2 | ❌ fail | significant regression past the effect floor (effect=-0.200, 95% CI [-0.211, -0.189], p=0.001) | `━━········│··········` |
| exact_answer | ✅ pass | no significant regression (effect=+0.000, 95% CI [+0.000, +0.000], p=1.000) | `··········╋··········` |

**2 passed, 1 failed, 0 inconclusive**

Wire it up with:

```yaml
name: regression
on: pull_request

jobs:
  signaltest:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write   # required to post the comment
    steps:
      - uses: actions/checkout@v4
      - uses: Falcon305/signaltest@v0.7.0
        with:
          install: pip install -e ".[dev]"
          paths: tests/regression
```

| Input | Default | Meaning |
|-------|---------|---------|
| `python-version` | `3.12` | Python to run on |
| `install` | `pip install -e .` | how to install your package and test deps |
| `paths` | *(all tests)* | paths or extra pytest args for your cases |
| `comment` | `true` | post the sticky PR comment |

The table is produced from a results file your tests write with
`pytest --signaltest-json results.json`; `signaltest report results.json`
renders it (`--format text`, `html`, or `junit` too), so you can reproduce the
exact comment locally. Use `--format junit` to emit a JUnit XML file that GitHub,
GitLab, and Jenkins render natively in their test UI.

## Gating scores from other tools

Already running evals in Inspect AI, DeepEval, Ragas, or your own harness?
signaltest is happy to be just the decision layer. If you can produce two arrays
of per-sample scores — a baseline and a candidate — `compare_scores` applies the
same significance + effect-size gate without the `Case` machinery:

```python
from signaltest import compare_scores

verdict = compare_scores(baseline_scores, candidate_scores, kind="numeric")
print(verdict.status, verdict.reason)
```

There are adapters for the two most common sources. Inspect AI repeats each
sample with epochs; DeepEval gives a metric score per test — both produce exactly
the arrays the gate wants:

```python
from signaltest import compare_scores, scores_from_inspect_log, scores_from_deepeval

base = scores_from_inspect_log(baseline_log, "accuracy")
cand = scores_from_inspect_log(candidate_log, "accuracy")
compare_scores(base, cand, kind="numeric")
```

This is the natural companion to tools that already repeat each case (Inspect's
epochs, DeepEval's runs, Braintrust's trials) but only average the results —
hand signaltest the raw samples and get a real verdict.

When both arrays score the **same inputs in the same order**, pass `paired=True`.
A matched comparison (Wilcoxon signed-rank) removes the variance between inputs,
so a small but consistent regression is caught with far fewer samples than an
unpaired test would need:

```python
compare_scores(base, cand, kind="numeric", paired=True)
```

To see *which* inputs drove a regression rather than just the aggregate verdict,
`top_regressions` returns the matched examples that dropped most:

```python
from signaltest import top_regressions

for index, delta in top_regressions(base, cand):
    print(f"sample #{index} dropped {delta:+.2f}")
```

## CLI

```sh
signaltest init                             # scaffold a starter test (--workflow for CI too)
signaltest version
signaltest baselines baselines/agent.json   # list recorded cases
signaltest show baselines/agent.json math::exact_match
signaltest rm baselines/agent.json math::exact_match   # drop one baseline entry
signaltest report results.json              # markdown table (--format text|html|junit)
signaltest power baselines/agent.json math::exact_match --min-effect 0.1
signaltest trends history.jsonl             # pass/fail of each case over time
```

To build that history, append each run's verdicts with
`pytest --signaltest-history history.jsonl`; `signaltest trends` then shows a
per-case sparkline of recent results.

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
python examples/flaky.py       # threshold vs. statistical gate, side by side
```

For a full run against a live model — sequential sampling, paired comparison, and
`top_regressions` on a real Claude agent — see
[examples/real_agent/](examples/real_agent/) (needs `ANTHROPIC_API_KEY`).

See [docs/architecture.md](docs/architecture.md) for how the pieces fit together
and how to add your own metric.

## FAQ

**Does it call my LLM?** Only through the `run` function you provide. signaltest
never talks to a provider itself.

**Can `run` be async?** Yes. If `run` is an `async def`, signaltest awaits it for
each sample, so coroutine-based agents work with no wrapper.

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
