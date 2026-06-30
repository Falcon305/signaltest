# Benchmark: signaltest vs naive threshold gates

Does the statistical gate actually beat a threshold? This is a Monte Carlo that
measures it. Each trial simulates one CI run — `n=10` scored runs of a baseline
and a candidate, with run-to-run noise — and asks three gates to decide PASS/FAIL:

- **naive (any drop)** — fail if the candidate mean is below the baseline mean.
- **naive (2% margin)** — fail if the mean dropped by more than 2 points.
- **signaltest** — `compare_scores(..., min_effect=0.02)`: fail only on a
  statistically significant drop past the 2-point floor.

Reproduce with `python benchmark/simulate.py` (offline, seeded, 500 trials).

## False alarms on pure noise

The candidate is drawn from the *same* distribution as the baseline — nothing
really changed, so every FAIL here is a false alarm. The three rows raise the
run-to-run noise.

| run-to-run noise (σ) | naive (any drop) | naive (2% margin) | signaltest |
| --- | --- | --- | --- |
| 0.02 | 50% | 1% | 0% |
| 0.04 | 54% | 13% | 2% |
| 0.06 | 53% | 25% | 2% |

The "any drop" gate fails about half the time on noise alone — useless. The fixed
2% margin is fine when it's tuned to the noise (σ=0.02), but as the metric gets
noisier the *same* threshold starts false-alarming: 1% → 13% → 25%. signaltest
calibrates to whatever noise is present and holds its false-alarm rate near the
0.05 it was asked for, at every noise level, with no retuning.

## Catching a real regression

Now the candidate is genuinely 6 points worse. A FAIL is a correct catch.

| run-to-run noise (σ) | naive (any drop) | naive (2% margin) | signaltest |
| --- | --- | --- | --- |
| 0.02 | 100% | 100% | 100% |
| 0.04 | 100% | 99% | 90% |
| 0.06 | 99% | 94% | 57% |

At low noise everything catches it. At high noise the naive gates look better —
but only because they fail on *everything*: at σ=0.06 the 2% margin "catches" 94%
of regressions while also flagging 25% of pure noise. You can't read a catch rate
without its false-alarm rate.

At σ=0.06 with only 10 runs, a 6-point drop genuinely isn't reliably separable
from noise, and signaltest says so — it returns `inconclusive` and tells you to
sample more, rather than flipping a coin and calling it a regression. Give it the
samples (raise `n`, or let sequential mode draw them) and the catch rate climbs
while the false-alarm rate stays put. That trade — calibrated honesty over
trigger-happy guessing — is the whole point.
