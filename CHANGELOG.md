# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

### Added
- Sequential mode spends alpha with an O'Brien-Fleming schedule by default (almost
  none early, most at the final look), so early stops need strong evidence but the
  final decision keeps nearly full power. `spending="pocock"` keeps the even split.
- Sequential mode honors `workers`: each look's batch is sampled concurrently, and
  because the draw order is preserved the verdict is identical to single-threaded.

### Changed
- A sequential `run_suite` now spends alpha across the cases as well as the looks,
  so suite-wide false positives stay bounded under early stopping (the multiplicity
  protection the fixed-sample path gets from Benjamini-Hochberg). Single-case
  `check_case` / `assert_no_regression` are unaffected.

## 0.6.0 - 2026-06-30

### Added
- Sequential testing: `sequential=True` (with `max_n` and `looks`) draws samples
  in batches and stops as soon as the gate is conclusive, spending alpha across
  the looks so early stopping does not inflate false positives. A verdict now
  reports how many `samples` it took.
- Paired comparison: `compare_scores(..., paired=True)` uses a Wilcoxon
  signed-rank test and paired bootstrap CI for matched per-input scores, removing
  between-input variance so a consistent shift is detected with fewer samples.
- `top_regressions(baseline, candidate)` returns the inputs that dropped most, so
  reports can show which examples drove a regression.

### Changed
- Reports list failures first, then inconclusive, then passes, with the biggest
  drop on top.

## 0.5.0 - 2026-06-30

### Added
- Project-wide defaults in `pyproject.toml` under `[tool.signaltest]` (n, alpha,
  min_effect, min_valid, workers, test); an explicit argument still wins.
- Run history: `pytest --signaltest-history history.jsonl` appends each run's
  verdicts, and `signaltest trends` shows a per-case sparkline over time.

### Changed
- The GitHub Action installs `pytest`, so it runs even when the project's install
  command does not include a test runner.

### Added
- Every measured case carries a bootstrap 95% confidence interval for the
  effect, shown in reports as numbers and as a visual bar (`ci_bar`).
- `test="mannwhitney"` selects a rank-based numeric significance test alongside
  the default permutation test.
- Async agents: a `run` coroutine is awaited for each sample.

### Changed
- The effect confidence interval uses the percentile bootstrap, which is robust
  on constant score arrays (no more degenerate-data warnings).

### Added
- Adapters to gate scores from other tools: `scores_from_inspect_log` and
  `scores_from_deepeval` feed `compare_scores`.
- JUnit XML report output (`signaltest report --format junit`, `to_junit`) so CI
  systems render results natively.
- Opt-in parallel sampling via `workers=` on `check_case` / `run_suite`.
- `signaltest init` scaffolds a starter regression test and, with `--workflow`,
  a GitHub Actions workflow.

## 0.2.0 - 2026-06-30

### Added
- GitHub Action that runs your cases and posts a sticky results comment on the
  pull request, updated in place on every push.
- `pytest --signaltest-json PATH` writes the run's verdicts to JSON.
- `signaltest report` renders that JSON as markdown, plain text, or HTML.
- `compare_scores` gates two raw score arrays, so signaltest can sit on top of
  Inspect AI epochs, DeepEval runs, or any harness that already samples.
- Power advisor: `signaltest power`, and inconclusive verdicts now suggest how
  many samples would detect the effect you set.
- Result caching: a `cache` path plus a `cache_key` per case reuses sampled
  scores instead of re-running an expensive agent.
- Snapshot-style baseline updates: `pytest --signaltest-update`, an `update=`
  flag, and `signaltest rm` to drop a single entry.
- `Faithfulness` and `AnswerRelevancy` judge metrics (provider-agnostic).
- `to_markdown`, `to_html`, `write_json`, and `read_json` helpers in the public
  API.

## 0.1.0 - 2026-06-30

### Added
- Statistical gate: permutation and Fisher significance, bootstrap effect-size
  interval, Benjamini-Hochberg correction, and a decision that blocks only on a
  significant regression past a minimum effect size.
- Underpowered detection so cases with too few samples are flagged, not passed.
- Metrics: exact match, contains, numeric (configurable polarity), trajectory
  match, and an LLM-judge metric that wraps any scoring callable.
- `Metric` protocol so custom metrics need only `name`, `kind`, `polarity`, and
  `score`.
- Tool-trajectory model, match score, and a git-style diff renderer.
- Baseline JSON store with cold-start record-only and corrupt-file detection.
- Model versioning: baselines re-record on a model change instead of reporting it
  as a regression.
- pytest plugin and `assert_no_regression` for single cases.
- `run_suite` with suite-level correction, plus a text report and CI exit code.
- Reports show the measured effect size and p-value on every case.
- `signaltest` CLI for inspecting baselines.
- Type hints across the package, checked with mypy `strict`.
- Offline demos (a minimal case and a tool-using agent) and an end-to-end test
  that run with no API key.
