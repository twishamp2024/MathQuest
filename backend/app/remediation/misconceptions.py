"""Misconception Detection Heuristics for Children's Mathematical Thinking."""

import re
from typing import Optional, Dict
from fractions import Fraction
from backend.app.validators.math_validator import MathValidator


class MisconceptionDetector:
    """Detects systematic student misconceptions based on question type and submitted answer."""

    @classmethod
    def analyze(
        cls,
        concept_id: str,
        question_text: str,
        submitted: str,
        correct_answer: str,
    ) -> Optional[str]:
        """
        Identify if submitted incorrect answer matches known misconception patterns.
        """
        s_norm = MathValidator.normalize_string(submitted)
        c_norm = MathValidator.normalize_string(correct_answer)
        if s_norm == c_norm:
            return None

        # 1. Adding denominators in fractions (e.g. 1/4 + 2/4 = 3/8)
        if "add_sub_like_fractions" in concept_id or "add_sub_unlike_fractions" in concept_id:
            # Parse fractions in question: e.g. "What is 1/4 + 2/4?"
            fracs = re.findall(r"(\d+)/(\d+)", question_text)
            if len(fracs) >= 2:
                n1, d1 = int(fracs[0][0]), int(fracs[0][1])
                n2, d2 = int(fracs[1][0]), int(fracs[1][1])
                if "+" in question_text:
                    added_den_str = f"{n1 + n2}/{d1 + d2}"
                    if s_norm == added_den_str or s_norm == f"{n1 + n2} / {d1 + d2}":
                        return "You added the denominators together! In fraction addition, the bottom denominator stays the same when it represents parts of the same whole."

        # 2. PEMDAS / Order of operations left-to-right error (e.g. 3 + 4 * 5 = 35 instead of 23)
        if "order_of_operations" in concept_id:
            match = re.search(r"(\d+)\s*\+\s*(\d+)\s*[×*]\s*(\d+)", question_text)
            if match:
                a, b, c = int(match.group(1)), int(match.group(2)), int(match.group(3))
                left_to_right = (a + b) * c
                if s_norm == str(left_to_right):
                    return "You added before multiplying! Remember the Order of Operations (PEMDAS): multiplication always comes before addition."

        # 3. Perimeter vs Area confusion
        if "perimeter" in concept_id:
            # Check if student multiplied dimensions instead of adding
            dims = [int(x) for x in re.findall(r"\b(\d+)\b", question_text)]
            if len(dims) >= 2:
                product = dims[0] * dims[1]
                if s_norm == str(product):
                    return "You multiplied the sides (which finds Area) instead of adding all boundary sides (which gives Perimeter)!"

        if "area" in concept_id:
            # Check if student calculated perimeter instead of multiplying
            dims = [int(x) for x in re.findall(r"\b(\d+)\b", question_text)]
            if len(dims) >= 2:
                perim = 2 * (dims[0] + dims[1])
                if s_norm == str(perim):
                    return "You added the side lengths (which finds Perimeter) instead of multiplying length × width (which gives Area)!"

        # 4. Decimals: Longer decimal assumed larger (e.g., choosing 0.125 over 0.5)
        if "decimal" in concept_id and "greater" in question_text:
            if "0.125" in s_norm or (len(s_norm) > len(c_norm) and float(s_norm) < float(c_norm)):
                return "Be careful with decimals: having more digits doesn't make a number larger. Compare the tenths place first!"

        # 5. Subtraction: subtracting smaller from larger ignoring order (e.g. 3 - 7 = 4 instead of -4)
        if "integers" in concept_id and "-" in question_text:
            match = re.search(r"(\d+)\s*-\s*(\d+)", question_text)
            if match:
                a, b = int(match.group(1)), int(match.group(2))
                if a < b and s_norm == str(b - a):
                    return "Notice the order of subtraction: subtracting a larger number from a smaller one results in a negative number."

        return None
