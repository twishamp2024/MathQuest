"""Tests for mathematical question & answer validation."""

from fractions import Fraction
from backend.app.validators.math_validator import MathValidator
from backend.app.schemas.question import GeneratedQuestionPayload


def test_answer_equivalence_exact():
    assert MathValidator.are_answers_equivalent("42", "42")
    assert MathValidator.are_answers_equivalent("  hello ", "HELLO")


def test_answer_equivalence_fractions():
    # 2/4 is equivalent to 1/2
    assert MathValidator.are_answers_equivalent("2/4", "1/2", "fraction")
    assert MathValidator.are_answers_equivalent(" 6 / 8 ", "3/4", "fraction")
    assert MathValidator.are_answers_equivalent("4/8", "2/4", "fraction")
    assert not MathValidator.are_answers_equivalent("2/5", "1/2", "fraction")


def test_answer_equivalence_floats():
    assert MathValidator.are_answers_equivalent("0.5", ".5", "float")
    assert MathValidator.are_answers_equivalent("3.80", "3.8", "float")
    assert not MathValidator.are_answers_equivalent("3.85", "3.8", "float")


def test_answer_equivalence_ratios():
    assert MathValidator.are_answers_equivalent("2:3", " 2 : 3 ", "text")
    assert MathValidator.are_answers_equivalent("4:6", "2:3", "text")


def test_validate_question_payload_valid():
    payload = GeneratedQuestionPayload(
        question_text="What is 5 + 7?",
        topic_id="add_sub",
        concept_id="add_single_digit",
        difficulty=1,
        question_format="multiple_choice",
        options=["10", "11", "12", "13"],
        correct_answer="12",
        expected_answer_type="integer",
    )
    is_valid, msg = MathValidator.validate_question_payload(payload)
    assert is_valid is True
    assert msg == "Valid"


def test_validate_question_payload_rejection_missing_answer():
    payload = GeneratedQuestionPayload(
        question_text="What is 5 + 7?",
        topic_id="add_sub",
        concept_id="add_single_digit",
        difficulty=1,
        question_format="multiple_choice",
        options=["10", "11", "13"],
        correct_answer="12",  # Not in options!
        expected_answer_type="integer",
    )
    is_valid, msg = MathValidator.validate_question_payload(payload)
    assert is_valid is False
    assert "not found in options" in msg


def test_validate_question_payload_rejection_division_by_zero():
    payload = GeneratedQuestionPayload(
        question_text="Calculate: 12 / 0",
        topic_id="mul_div",
        concept_id="basic_division",
        difficulty=2,
        question_format="multiple_choice",
        options=["0", "1", "12", "undefined"],
        correct_answer="undefined",
        expected_answer_type="text",
    )
    is_valid, msg = MathValidator.validate_question_payload(payload)
    assert is_valid is False
    assert "Division by zero" in msg
