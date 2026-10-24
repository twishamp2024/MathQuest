"""Tests for deterministic parameterized offline question generator."""

from backend.app.generators.offline_generator import OfflineQuestionGenerator
from backend.app.validators.math_validator import MathValidator
from backend.app.schemas.question import QuestionConstraint
from backend.app.engine.curriculum import CURRICULUM


def test_generator_all_10_topics_validity():
    gen = OfflineQuestionGenerator()

    for topic_id, topic in CURRICULUM.items():
        for concept in topic.concepts:
            for diff in concept.difficulty_levels[:2]:
                q_format = "comparison" if "compare" in concept.id else "multiple_choice"
                constraints = QuestionConstraint(
                    topic_id=topic_id,
                    concept_id=concept.id,
                    learning_objective=concept.learning_objective,
                    difficulty=diff,
                    question_format=q_format,
                    expected_answer_type="integer" if "fraction" not in concept.id else "fraction",
                )
                payload = gen.generate(constraints)
                is_valid, reason = MathValidator.validate_question_payload(payload)
                assert is_valid is True, f"Failed for {concept.id} diff {diff}: {reason}"
                assert len(payload.question_text) >= 5
                assert payload.correct_answer is not None
                if q_format in ("multiple_choice", "comparison"):
                    assert payload.options is not None
                    assert len(payload.options) == 4
                    # Correct answer must be among options
                    match = any(
                        MathValidator.are_answers_equivalent(payload.correct_answer, opt, payload.expected_answer_type)
                        for opt in payload.options
                    )
                    assert match is True
