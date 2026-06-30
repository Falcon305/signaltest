# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

### Added
- Statistical gate: permutation and Fisher significance, bootstrap effect-size
  interval, Benjamini-Hochberg correction, and a decision that blocks only on a
  significant regression past a minimum effect size.
- Underpowered detection so cases with too few samples are flagged, not passed.
- Metrics: exact match, contains, numeric (configurable polarity), trajectory match.
- Tool-trajectory model, match score, and a git-style diff renderer.
- Baseline JSON store with cold-start record-only and corrupt-file detection.
- Model versioning: baselines re-record on a model change instead of reporting it
  as a regression.
- pytest plugin and `assert_no_regression` for single cases.
- `run_suite` with suite-level correction, plus a text report and CI exit code.
- `signaltest` CLI for inspecting baselines.
- Offline demo and end-to-end test that run with no API key.
