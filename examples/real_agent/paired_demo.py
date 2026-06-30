"""Paired comparison on a real agent: a good prompt vs a regressed prompt.

    export ANTHROPIC_API_KEY=sk-...
    python examples/real_agent/paired_demo.py

Scores all 8 questions once under each prompt, then gates the matched scores.
Pairing removes the between-question variance, and top_regressions names the
questions that actually changed.
"""

import sys

from agent import GOOD_PROMPT, QUESTIONS, REGRESSED_PROMPT, ConciseAnswer, ask

from signaltest import compare_scores, top_regressions


def score_arm(prompt: str) -> list[float]:
    metric = ConciseAnswer()
    return [float(metric.score(ask(question, prompt), answer)) for question, answer in QUESTIONS]


def main() -> None:
    print(f"Scoring {len(QUESTIONS)} questions under each prompt (real API calls)...\n")
    baseline = score_arm(GOOD_PROMPT)
    candidate = score_arm(REGRESSED_PROMPT)

    verdict = compare_scores(baseline, candidate, kind="numeric", min_effect=0.1, paired=True)
    print("good prompt:     ", baseline)
    print("regressed prompt:", candidate)
    print(f"\nverdict: {verdict.status.upper()} — {verdict.reason}")

    worst = top_regressions(baseline, candidate)
    if worst:
        print("\nwhat regressed:")
        for index, delta in worst:
            print(f"  {delta:+.0f}  {QUESTIONS[index][0]}")


if __name__ == "__main__":
    sys.exit(main())
