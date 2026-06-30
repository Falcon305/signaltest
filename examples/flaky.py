"""Why a statistical gate beats a threshold.

Three scenarios, each comparing a naive "did the mean drop?" check against
signaltest's significance + effect-size gate. Fully deterministic, no API key.
"""

from signaltest import compare_scores
from signaltest.metrics.base import NUMERIC


def naive(baseline, candidate):
    """The check most teams start with: any drop in the mean fails CI."""
    return "FAIL" if sum(candidate) / len(candidate) < sum(baseline) / len(baseline) else "PASS"


def gate(baseline, candidate):
    return compare_scores(baseline, candidate, kind=NUMERIC, min_effect=0.03).status.upper()


def shift(scores, delta):
    return [s + delta for s in scores]


def main():
    base = [0.80, 0.81, 0.79, 0.80, 0.81, 0.79, 0.80, 0.80, 0.81, 0.79, 0.80, 0.80]
    noise = [0.80, 0.79, 0.81, 0.78, 0.82, 0.80, 0.79, 0.81, 0.78, 0.80, 0.81, 0.79]

    scenarios = [
        ("pure noise (same model)", base, noise),
        ("trivial 0.5% drift", base, shift(base, -0.005)),
        ("real 15% regression", base, shift(base, -0.15)),
    ]

    print(f"{'scenario':<26} {'naive threshold':<16} {'signaltest':<12}")
    print("-" * 56)
    for name, baseline, candidate in scenarios:
        print(f"{name:<26} {naive(baseline, candidate):<16} {gate(baseline, candidate):<12}")

    print()
    print("The threshold fails CI on noise and on meaningless drift.")
    print("signaltest stays green until a regression is real and large enough.")


if __name__ == "__main__":
    main()
