"""Tests for AI provider abstraction and automatic offline fallback."""

from unittest.mock import patch
from backend.app.generators.ai_generator import AIQuestionGenerator
from backend.app.schemas.question import QuestionConstraint


def test_ai_generator_offline_mode_default():
    # In offline mode, immediately returns offline question
    ai_gen = AIQuestionGenerator()
    constraints = QuestionConstraint(
        topic_id="add_sub",
        concept_id="add_single_digit",
        learning_objective="Recall single-digit addition sums",
        difficulty=1,
        question_format="multiple_choice",
        expected_answer_type="integer",
    )
    payload, source = ai_gen.generate(constraints)
    assert source == "offline"
    assert payload.correct_answer is not None


def test_ai_generator_exception_fallback():
    ai_gen = AIQuestionGenerator()
    ai_gen.provider = "gemini"
    ai_gen.api_key = "dummy_key_for_test"

    # Mock _call_ai_provider raising an exception (e.g. network timeout or API error)
    with patch.object(ai_gen, "_call_ai_provider", side_effect=RuntimeError("Connection timeout")):
        constraints = QuestionConstraint(
            topic_id="mul_div",
            concept_id="multiplication_facts",
            learning_objective="Recall times tables",
            difficulty=2,
            question_format="multiple_choice",
            expected_answer_type="integer",
        )
        payload, source = ai_gen.generate(constraints)
        # Should gracefully fall back to offline generator
        assert source == "offline_fallback"
        assert payload.question_text is not None
        assert payload.correct_answer is not None
