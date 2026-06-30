# Real-agent demo

An end-to-end run of signaltest against an actual Claude model, not synthetic
numbers. It shows the three things signaltest is for, on a real agent:

- **Sequential sampling** keeps the cost down — unchanged questions settle in a
  few calls instead of a fixed `n`.
- **Paired comparison** gates the good prompt against a regressed one with the
  matched per-question scores.
- **`top_regressions`** names the questions that actually changed.

The agent is a tiny trivia QA loop (`agent.py`). The "regression" is a prompt
change that swaps bare answers for chatty sentences — a format break that fails
downstream parsing, which is one of the most common real prompt regressions.

## Setup

```sh
pip install signaltest anthropic
export ANTHROPIC_API_KEY=sk-...
```

These make real API calls and cost money. The dataset is 8 questions to keep a
run cheap; set `SIGNALTEST_MODEL` to pick a model (defaults to `claude-sonnet-4-6`).

## Paired comparison + what regressed

```sh
python examples/real_agent/paired_demo.py
```

Illustrative output:

```
good prompt:      [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
regressed prompt: [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0]

verdict: FAIL — significant regression past the effect floor

what regressed:
  -1  What is the chemical symbol for gold?
  -1  How many continents are there?
  -1  What planet is known as the Red Planet?
  ...
```

## The full CI loop

```sh
# 1. record the baseline on the good prompt
pytest examples/real_agent/test_quality.py

# 2. ship a bad prompt change — the gate goes red
SIGNALTEST_PROMPT=regressed pytest examples/real_agent/test_quality.py -s
```

The first run cold-starts the baseline (everything passes). The second run scores
the regressed prompt against that baseline and fails the build, printing which
questions regressed. Delete `baselines/qa.json` to reset.
