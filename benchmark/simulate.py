"""Monte Carlo: signaltest vs naive threshold gates.

Each trial simulates one CI run — `n` scored runs of a baseline and a candidate,
with run-to-run noise — and asks each gate to decide PASS or FAIL. Over many
trials we measure:

  - false alarms: the candidate is drawn from the SAME distribution as the
    baseline (nothing really changed); a good gate should rarely FAIL.
  - catches: the candidate is genuinely worse; a good gate should FAIL.

The point is robustness to noise. A fixed threshold has to be tuned to the
metric's noise level; when the metric gets noisier the same threshold starts
false-alarming. signaltest calibrates to whatever noise is present and holds its
false-alarm rate near alpha without tuning.

Fully offline and seeded. Run it yourself:

    python benchmark/simulate.py
"""

import numpy as np

from signaltest import compare_scores

TRIALS = 500
N = 10
BASELINE = 0.80
ALPHA = 0.05
MARGIN = 0.02  # the fixed drop a naive gate tolerates; also signaltest's effect floor
NOISE_LEVELS = [0.02, 0.04, 0.06]
REGRESSION = 0.06  # a real six-point drop


def naive_any(base: np.ndarray, cand: np.ndarray) -> bool:
    return bool(cand.mean() < base.mean())


def naive_margin(base: np.ndarray, cand: np.ndarray) -> bool:
    return bool(base.mean() - cand.mean() > MARGIN)


def signaltest_gate(base: np.ndarray, cand: np.ndarray) -> bool:
    verdict = compare_scores(base, cand, kind="numeric", min_effect=MARGIN, alpha=ALPHA)
    return verdict.status == "fail"


GATES = [
    ("naive (any drop)", naive_any),
    ("naive (2% margin)", naive_margin),
    ("signaltest", signaltest_gate),
]


def fail_rate(rng: np.random.Generator, candidate_mean: float, sigma: float) -> list[float]:
    fails = [0, 0, 0]
    for _ in range(TRIALS):
        base = np.clip(rng.normal(BASELINE, sigma, N), 0.0, 1.0)
        cand = np.clip(rng.normal(candidate_mean, sigma, N), 0.0, 1.0)
        for i, (_, gate) in enumerate(GATES):
            fails[i] += gate(base, cand)
    return [f / TRIALS for f in fails]


def table(title: str, candidate_mean: float) -> str:
    rng = np.random.default_rng(0)
    header = "| run-to-run noise (σ) | " + " | ".join(name for name, _ in GATES) + " |"
    rule = "| --- | " + " | ".join("---" for _ in GATES) + " |"
    rows = [header, rule]
    for sigma in NOISE_LEVELS:
        rates = fail_rate(rng, candidate_mean, sigma)
        cells = " | ".join(f"{r:.0%}" for r in rates)
        rows.append(f"| {sigma:.2f} | {cells} |")
    return f"### {title}\n\n" + "\n".join(rows)


def main() -> None:
    print(f"{TRIALS} trials, n={N} runs per side, baseline accuracy {BASELINE:.0%}\n")
    print(table("False alarms on pure noise (FAIL rate, lower is better)", BASELINE))
    print()
    print(
        table(
            f"Catching a real {REGRESSION:.0%} regression (FAIL rate, higher is better)",
            BASELINE - REGRESSION,
        )
    )


if __name__ == "__main__":
    main()
