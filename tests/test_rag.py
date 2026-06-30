from signaltest.metrics.base import HIGHER_BETTER, NUMERIC
from signaltest.metrics.rag import AnswerRelevancy, Faithfulness


def test_faithfulness_scores_with_context():
    seen = {}

    def judge(answer, context):
        seen["answer"] = answer
        seen["context"] = context
        return 0.9

    metric = Faithfulness(judge=judge)
    assert metric.score("the sky is blue", "sky=blue") == 0.9
    assert seen == {"answer": "the sky is blue", "context": "sky=blue"}
    assert metric.name == "faithfulness"
    assert metric.kind == NUMERIC
    assert metric.polarity == HIGHER_BETTER


def test_answer_relevancy_scores_with_question():
    metric = AnswerRelevancy(judge=lambda answer, question: 1, name="relevancy")
    score = metric.score("Paris", "capital of France?")
    assert isinstance(score, float)
    assert score == 1.0
    assert metric.name == "relevancy"
