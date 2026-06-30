# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

### Added
- GitHub Action that runs your cases and posts a sticky results comment on the
  pull request, updated in place on every push.
- `pytest --signaltest-json PATH` writes the run's verdicts to JSON.
- `signaltest report` renders that JSON as a markdown table or plain text.
- `to_markdown`, `write_json`, and `read_json` helpers in the public API.

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
