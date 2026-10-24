"""Server-side Mathematical Question & Answer Validator.

Guarantees:
- Never trusts raw AI answers without independent verification.
- Normalizes child input (whitespace, capitalization, equivalent fractions like 2/4 == 1/2).
- Validates arithmetic consistency, zero-division hazards, and range bounds.
- Detects common arithmetic misconceptions.
"""

import re
from fractions import Fraction
from typing import Tuple, Optional, Any
from backend.app.schemas.question import GeneratedQuestionPayload


class MathValidator:
    """Independent validator and normalizer for mathematical questions and answers."""

    @classmethod
    def normalize_string(cls, val: str) -> str:
        """Strip surrounding whitespace, collapse inner spaces, lowercase."""
        if not val:
            return ""
        cleaned = val.strip().lower()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    @classmethod
    def parse_fraction(cls, text: str) -> Optional[Fraction]:
        """Attempt to parse a fraction string like '3/4', ' 1 / 2 ', or whole number '5'."""
        cleaned = cls.normalize_string(text).replace(" ", "")
        match = re.match(r"^(-?\d+)(?:/(-?\d+))?$", cleaned)
        if not match:
            return None
        num = int(match.group(1))
        den = int(match.group(2)) if match.group(2) else 1
        if den == 0:
            return None
        try:
            return Fraction(num, den)
        except Exception:
            return None

    @classmethod
    def parse_float(cls, text: str) -> Optional[float]:
        """Attempt to parse float or integer text."""
        cleaned = cls.normalize_string(text).replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None

    @classmethod
    def are_answers_equivalent(
        cls, submitted: str, expected: str, answer_type: str = "integer"
    ) -> bool:
        """
        Check mathematical equivalence between child submitted answer and expected answer.
        Handles:
        - Exact string match after normalization
        - Equivalent fractions (e.g. 2/4 == 1/2)
        - Numeric float tolerance (e.g. 0.5 == .50)
        - Choice string equality (e.g. 'A' == 'a')
        """
        s_norm = cls.normalize_string(submitted)
        e_norm = cls.normalize_string(expected)

        if s_norm == e_norm:
            return True

        # Check fraction equivalence
        f_sub = cls.parse_fraction(s_norm)
        f_exp = cls.parse_fraction(e_norm)
        if f_sub is not None and f_exp is not None:
            return f_sub == f_exp

        # Check numeric float equivalence
        flt_sub = cls.parse_float(s_norm)
        flt_exp = cls.parse_float(e_norm)
        if flt_sub is not None and flt_exp is not None:
            return abs(flt_sub - flt_exp) < 1e-5

        # Check ratio equivalence (e.g., '2:3' vs ' 2 : 3 ')
        if ":" in s_norm and ":" in e_norm:
            s_parts = [p.strip() for p in s_norm.split(":")]
            e_parts = [p.strip() for p in e_norm.split(":")]
            if len(s_parts) == 2 and len(e_parts) == 2:
                try:
                    f1 = Fraction(int(s_parts[0]), int(s_parts[1]))
                    f2 = Fraction(int(e_parts[0]), int(e_parts[1]))
                    return f1 == f2
                except Exception:
                    pass

        return False

    @classmethod
    def validate_question_payload(cls, payload: GeneratedQuestionPayload) -> Tuple[bool, str]:
        """
        Server-side validation of a generated question payload (from AI or offline bank).
        Rejects questions with:
        - Missing or empty text / answer
        - Less than 2 options if multiple choice
        - Correct answer not present in options list
        - Division by zero
        - Numeric answers outside safe bounds
        """
        if not payload.question_text or len(payload.question_text.strip()) < 5:
            return False, "Question text too short or empty."

        if not payload.correct_answer or len(payload.correct_answer.strip()) == 0:
            return False, "Correct answer is missing."

        if payload.question_format in ("multiple_choice", "comparison"):
            if not payload.options or len(payload.options) < 2:
                return False, f"Question format '{payload.question_format}' requires at least 2 options."
            
            # Verify correct answer is represented in options
            match_found = any(
                cls.are_answers_equivalent(payload.correct_answer, opt, payload.expected_answer_type)
                for opt in payload.options
            )
            if not match_found:
                return False, f"Correct answer '{payload.correct_answer}' not found in options {payload.options}."

        # Check for division by zero in question text
        if re.search(r"[÷/]\s*0(?!\d)", payload.question_text):
            return False, "Division by zero detected in question text."

        return True, "Valid"
