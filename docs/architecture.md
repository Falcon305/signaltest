# Architecture

This document explains how signaltest is put together and why. It is aimed at
contributors and at anyone deciding whether the tool fits their setup.

## The problem

An LLM agent is a stochastic function. Run the same prompt twice and the score
moves. A regression check that compares a single score against a fixed threshold
therefore fails at random: the build goes red on an unlucky draw, the team loses
trust, and the check is deleted. signaltest exists to make that check trustworthy
— it should fire on a real regression and stay quiet on noise.

## The idea

Treat each case's score as a distribution rather than a number.

1. Sample the candidate agent `n` times.
2. Compare those samples against `n` recorded baseline samples.
3. Fail only when the difference is **statistically significant** *and* clears a
   **minimum effect size**.

Significance alone is not enough — with enough samples a trivial 0.1% shift is
"significant." The effect floor is what keeps meaningless drift green.

## The pipeline

```
        Case.run() ──► metric.score() ──► candidate samples ─┐
                                                             ├─► significance test
   baseline JSON ──► recorded samples ───────────────────────┘        │
                                                                       ▼
                                              effect size ───────► gate decision
                                                                       │
                                              (suite) BH correction ───┤
                                                                       ▼
                                                            PASS / FAIL / INCONCLUSIVE
```

## Modules

| Package | Responsibility |
|---------|----------------|
| `metrics/` | Turn an agent output into a score. `Metric` is a `Protocol`: any object with `name`, `kind`, `polarity`, and `score(output, expected)` works. |
| `stats/significance` | Permutation test (numeric) and Fisher's exact test (boolean). Both seeded — the flake-killer must not flake. |
| `stats/effect` | Bootstrap confidence interval for the mean difference. |
| `stats/correction` | Benjamini-Hochberg FDR adjustment across a suite. |
| `stats/gate` | `decide_gate` combines p-value, effect, polarity, power, and validity into a `Verdict`. |
| `baseline/` | Load and store recorded samples as JSON, fail loud on corruption. |
| `runner` | Orchestrates: sample, look up or record the baseline, measure, decide. `check_case`, `assert_no_regression`, `run_suite`. |
| `report` | Human-readable summary, including effect size and p-value. |
| `cli` / `plugin` | `signaltest` command and the pytest entry point. |

## Key decisions

**Baseline is stored samples, not live re-execution.** The baseline is `n`
recorded scores committed to the repo as JSON. We do not re-run an "old" agent at
test time — that would be slow, non-reproducible, and often impossible once a
prompt has changed. Accepting a new baseline is an explicit, reviewable diff.

**Significance is seeded.** The permutation test takes a fixed `rng`, so the same
inputs always yield the same p-value. A flaky flake-detector would defeat the
purpose.

**Effect floor before failing.** A regression must clear `min_effect` (defaults:
0.03 numeric, 0.10 boolean). This is the second half of the noise filter.

**Suite-level FDR.** Across many cases the chance of one false positive grows, so
p-values are adjusted with Benjamini-Hochberg before the gate sees them.

**Underpowered cases are inconclusive, never green.** If the sample sizes are too
small for any result to reach `alpha`, the case is flagged rather than passed
silently.

**Model versioning.** A baseline records the model it was captured under. Passing
a new `model=` that differs re-records the baseline instead of reporting a
regression, so a provider model swap can't masquerade as one.

## Extending it

Add a metric by writing a class that satisfies the `Metric` protocol:

```python
from signaltest.metrics.base import NUMERIC, HIGHER_BETTER

class WordCount:
    name = "word_count"
    kind = NUMERIC
    polarity = HIGHER_BETTER

    def score(self, output, expected):
        return float(len(output.split()))
```

`kind` selects the significance test; `polarity` tells the gate which direction
counts as a regression. Nothing else needs to change.
