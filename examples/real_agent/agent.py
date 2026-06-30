"""A tiny trivia agent backed by a real Claude model, with a regressed variant.

The two system prompts differ only in output *format*: the good one returns the
bare answer, the regressed one wraps it in a chatty sentence. A format change
that breaks downstream parsing is one of the most common real prompt regressions,
and it makes the demo fully legible without depending on the model being wrong.

Real API calls cost money; the dataset is 8 questions to keep a run cheap.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anthropic import Anthropic

MODEL = os.environ.get("SIGNALTEST_MODEL", "claude-sonnet-4-6")

GOOD_PROMPT = (
    "You are a precise trivia assistant. Answer with ONLY the shortest exact "
    "answer: a name, number, or single word. No sentences, no punctuation, "
    "no extra words."
)

REGRESSED_PROMPT = (
    "You are a friendly assistant. Answer conversationally in a full sentence, "
    "restating the question and adding a little helpful context."
)

QUESTIONS = [
    ("What is the chemical symbol for gold?", "Au"),
    ("How many continents are there?", "7"),
    ("What planet is known as the Red Planet?", "Mars"),
    ("Who wrote the play Romeo and Juliet?", "Shakespeare"),
    ("What is the capital of Japan?", "Tokyo"),
    ("What gas do plants primarily absorb?", "Carbon dioxide"),
    ("How many sides does a hexagon have?", "6"),
    ("What is the largest ocean on Earth?", "Pacific"),
]

_client: Anthropic | None = None


def _client_once() -> Anthropic:
    global _client
    if _client is None:
        from anthropic import Anthropic

        _client = Anthropic()
    return _client


def ask(question: str, system_prompt: str, model: str = MODEL) -> str:
    message = _client_once().messages.create(
        model=model,
        max_tokens=64,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )
    return message.content[0].text.strip()


class ConciseAnswer:
    """Pass only if the first line, normalized, equals the expected answer.

    A custom metric is just an object with name/kind/polarity and a score method.
    """

    name = "concise_answer"
    kind = "boolean"
    polarity = "higher_better"

    def score(self, output: str, expected: str) -> bool:
        first_line = output.strip().splitlines()[0] if output.strip() else ""
        normalized = first_line.lower().strip(" .!?\"'")
        return normalized == expected.lower()
