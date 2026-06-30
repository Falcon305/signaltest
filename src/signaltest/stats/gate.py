from dataclasses import dataclass
from math import comb

PASS = "pass"
FAIL = "fail"
INCONCLUSIVE = "inconclusive"


@dataclass
class Verdict:
    status: str
    pvalue: float
    effect: float
    reason: str


def decide_gate(
    pvalue,
    effect,
    *,
    polarity="higher_better",
    alpha=0.05,
    min_effect=0.0,
    n_valid,
    min_valid=2,
    underpowered=False,
):
    if n_valid < min_valid:
        return Verdict(INCONCLUSIVE, pvalue, effect, f"only {n_valid} valid runs, need {min_valid}")

    regressed = effect < 0 if polarity == "higher_better" else effect > 0
    significant = pvalue < alpha
    big_enough = abs(effect) >= min_effect

    if regressed and significant and big_enough:
        return Verdict(FAIL, pvalue, effect, "significant regression past the effect floor")
    if underpowered:
        return Verdict(INCONCLUSIVE, pvalue, effect, "underpowered, increase samples")
    return Verdict(PASS, pvalue, effect, "no significant regression")


def is_underpowered(n_baseline, n_candidate, alpha=0.05):
    smallest_possible_p = 2 / comb(n_baseline + n_candidate, n_baseline)
    return smallest_possible_p > alpha
