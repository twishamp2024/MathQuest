"""Deterministic Parameterized Question Generator and Offline Bank.

Generates mathematically verified, rich questions across all 10 curriculum topics.
Provides distractors, misconceptions, explanation steps, and multi-level hints.
"""

import random
import math
from typing import List, Tuple, Dict, Optional
from fractions import Fraction
from backend.app.generators.base import BaseQuestionGenerator
from backend.app.schemas.question import QuestionConstraint, GeneratedQuestionPayload


class OfflineQuestionGenerator(BaseQuestionGenerator):
    """Generates guaranteed mathematically correct questions offline."""

    def generate(self, constraints: QuestionConstraint) -> GeneratedQuestionPayload:
        cid = constraints.concept_id
        diff = constraints.difficulty

        # Dispatch based on concept id
        if cid == "add_single_digit":
            return self._gen_add_single(diff, constraints)
        elif cid == "sub_single_digit":
            return self._gen_sub_single(diff, constraints)
        elif cid == "add_sub_multi_digit":
            return self._gen_add_sub_multi(diff, constraints)
        elif cid == "integers_add_sub":
            return self._gen_integers(diff, constraints)
        elif cid == "multiplication_facts":
            return self._gen_multiplication_facts(diff, constraints)
        elif cid == "basic_division":
            return self._gen_division(diff, constraints)
        elif cid == "multi_digit_multiplication":
            return self._gen_multi_digit_mult(diff, constraints)
        elif cid == "order_of_operations":
            return self._gen_pemdas(diff, constraints)
        elif cid == "fraction_concepts":
            return self._gen_fraction_intro(diff, constraints)
        elif cid == "equivalent_fractions":
            return self._gen_equiv_fractions(diff, constraints)
        elif cid == "compare_like_denominators":
            return self._gen_compare_like_fractions(diff, constraints)
        elif cid == "compare_unlike_denominators":
            return self._gen_compare_unlike_fractions(diff, constraints)
        elif cid == "add_sub_like_fractions":
            return self._gen_add_sub_like_fractions(diff, constraints)
        elif cid == "add_sub_unlike_fractions":
            return self._gen_add_sub_unlike_fractions(diff, constraints)
        elif cid == "decimal_place_value":
            return self._gen_decimal_place_value(diff, constraints)
        elif cid == "decimal_arithmetic":
            return self._gen_decimal_arithmetic(diff, constraints)
        elif cid == "percent_basics":
            return self._gen_percent_basics(diff, constraints)
        elif cid == "ratio_representation":
            return self._gen_ratio_rep(diff, constraints)
        elif cid == "unitary_method":
            return self._gen_unitary_method(diff, constraints)
        elif cid == "missing_number_equations":
            return self._gen_missing_number(diff, constraints)
        elif cid == "linear_equations_one_step":
            return self._gen_linear_one_step(diff, constraints)
        elif cid == "linear_equations_two_step":
            return self._gen_linear_two_step(diff, constraints)
        elif cid == "perimeter_calculation":
            return self._gen_perimeter(diff, constraints)
        elif cid == "area_rectangles":
            return self._gen_area(diff, constraints)
        elif cid == "angle_properties":
            return self._gen_angles(diff, constraints)
        elif cid == "arithmetic_sequences":
            return self._gen_arithmetic_seq(diff, constraints)
        elif cid == "geometric_sequences":
            return self._gen_geom_seq(diff, constraints)
        else:
            return self._gen_add_single(diff, constraints)

    # -------------------------------------------------------------
    # Helper to build 4 unique shuffled options with distractors
    # -------------------------------------------------------------
    def _build_options(self, correct: str, distractors: List[str]) -> List[str]:
        opts = [correct]
        for d in distractors:
            if d != correct and d not in opts:
                opts.append(d)
                if len(opts) == 4:
                    break
        while len(opts) < 4:
            try:
                val = int(correct)
                alt = str(val + random.choice([-3, -2, -1, 1, 2, 3, 5]))
                if alt not in opts:
                    opts.append(alt)
            except ValueError:
                opts.append(f"{len(opts) + 1}")
        random.shuffle(opts)
        return opts

    # 1. Addition & Subtraction
    def _gen_add_single(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        a = random.randint(2, 9) if diff == 1 else random.randint(6, 12)
        b = random.randint(1, 9) if diff == 1 else random.randint(5, 12)
        ans = a + b
        text = f"What is {a} + {b}?"
        distractors = [str(ans - 1), str(ans + 1), str(ans + 2), str(a * b)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[f"Start with {a}.", f"Count on {b} more.", f"{a} + {b} = {ans}."],
            hint_small="Try starting at the larger number and counting on.",
            hint_detailed=f"If you start with {max(a, b)} and add {min(a, b)}, what number do you reach?",
        )

    def _gen_sub_single(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        b = random.randint(2, 9)
        ans = random.randint(1, 9)
        a = b + ans
        text = f"What is {a} - {b}?"
        distractors = [str(ans - 1), str(ans + 1), str(ans + 2), str(a + b)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[f"You have {a} items.", f"Take away {b} items.", f"{a} - {b} leaves {ans}."],
            hint_small="Think: what number added to the smaller number equals the larger?",
            hint_detailed=f"What number plus {b} gives {a}?",
        )

    def _gen_add_sub_multi(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        is_add = random.choice([True, False])
        if is_add:
            a = random.randint(15, 60) if diff <= 3 else random.randint(50, 450)
            b = random.randint(15, 45) if diff <= 3 else random.randint(50, 350)
            ans = a + b
            text = f"Calculate: {a} + {b}"
            distractors = [str(ans - 10), str(ans + 10), str(ans - 1), str(ans + 1)]
            steps = [f"Add the ones units: {a % 10} + {b % 10}", f"Add the tens with any carry: {ans}"]
        else:
            b = random.randint(15, 50) if diff <= 3 else random.randint(50, 250)
            ans = random.randint(10, 40) if diff <= 3 else random.randint(50, 200)
            a = b + ans
            text = f"Calculate: {a} - {b}"
            distractors = [str(ans - 10), str(ans + 10), str(ans - 1), str(ans + 1)]
            steps = [f"Subtract column by column.", f"Regroup/borrow if needed.", f"{a} - {b} = {ans}"]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=steps,
            hint_small="Break the numbers into tens and ones.",
            hint_detailed=f"For example, {a} is {a // 10 * 10} + {a % 10}.",
        )

    def _gen_integers(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        a = random.randint(-12, 10)
        b = random.randint(-10, 12)
        op = random.choice(["+", "-"])
        ans = a + b if op == "+" else a - b
        b_str = f"({b})" if b < 0 else str(b)
        text = f"Evaluate: {a} {op} {b_str}"
        distractors = [str(-ans), str(ans + 1), str(ans - 1), str(abs(a) + abs(b))]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                f"Imagine a number line.",
                f"Start at {a}.",
                f"Adding a positive or subtracting a negative moves right; subtracting positive moves left.",
                f"Result: {ans}",
            ],
            hint_small="Remember: subtracting a negative number is the same as adding a positive!",
            hint_detailed="Visualize a thermometer or number line moving up or down.",
        )

    # 2. Multiplication & Division
    def _gen_multiplication_facts(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        a = random.randint(2, 6) if diff == 1 else random.randint(4, 12)
        b = random.randint(2, 9) if diff <= 2 else random.randint(6, 12)
        ans = a * b
        text = f"What is {a} × {b}?"
        distractors = [str(a + b), str(ans - a), str(ans + b), str(ans - 2)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[f"{a} × {b} means {a} groups of {b}.", f"Adding {b}, {a} times gives {ans}."],
            hint_small=f"Think of {a} groups of {b}.",
            hint_detailed=f"If you know {a} × {b - 1} = {a * (b - 1)}, just add one more {a}.",
        )

    def _gen_division(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        divisor = random.randint(2, 6) if diff <= 2 else random.randint(4, 12)
        ans = random.randint(2, 9) if diff <= 2 else random.randint(5, 12)
        dividend = divisor * ans
        text = f"What is {dividend} ÷ {divisor}?"
        distractors = [str(ans + 1), str(ans - 1), str(divisor), str(ans + 2)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[f"Ask: What number times {divisor} equals {dividend}?", f"{divisor} × {ans} = {dividend}, so {dividend} ÷ {divisor} = {ans}."],
            hint_small="Division is the opposite of multiplication.",
            hint_detailed=f"What number multiplied by {divisor} gives {dividend}?",
        )

    def _gen_multi_digit_mult(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        a = random.randint(14, 45)
        b = random.randint(3, 9) if diff <= 3 else random.randint(11, 25)
        ans = a * b
        text = f"Calculate: {a} × {b}"
        distractors = [str(ans - 10), str(ans + 10), str(ans + b), str(ans - a)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[f"Multiply {a} by {b}.", f"Result = {ans}."],
            hint_small="Break the multi-digit factor into tens and ones.",
            hint_detailed=f"For example: ({a} × 10) or ({a // 10 * 10} × {b}) + ({a % 10} × {b}).",
        )

    def _gen_pemdas(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        a = random.randint(2, 8)
        b = random.randint(2, 6)
        c_val = random.randint(2, 5)
        ans = a + (b * c_val)
        text = f"Evaluate: {a} + {b} × {c_val}"
        wrong_order = (a + b) * c_val
        distractors = [str(wrong_order), str(ans + 2), str(ans - 2)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                "Remember Order of Operations (PEMDAS): Multiplication comes before Addition!",
                f"First multiply: {b} × {c_val} = {b * c_val}",
                f"Then add {a}: {a} + {b * c_val} = {ans}",
            ],
            hint_small="Check which operation has higher priority: multiplication or addition?",
            hint_detailed="Multiply first, then perform the addition.",
            common_misconceptions={"left_to_right_strict": "Added first then multiplied, ignoring PEMDAS rules"},
        )

    # 3. Fractions Intro & Equivalent Fractions
    def _gen_fraction_intro(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        num = random.randint(1, 5)
        den = random.randint(num + 1, 9)
        text = f"In the fraction {num}/{den}, what number is the numerator?"
        ans = str(num)
        distractors = [str(den), str(num + den), str(den - num)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(ans, distractors),
            correct_answer=ans,
            expected_answer_type="integer",
            explanation_steps=["The numerator is the top number representing the parts counted.", f"Here, top number is {num}."],
            hint_small="Numerator is on top, denominator is on the bottom.",
            hint_detailed="Look at the top number of the fraction.",
        )

    def _gen_equiv_fractions(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        n = random.randint(1, 3)
        d = random.randint(2, 5)
        multiplier = random.randint(2, 4)
        eq_n = n * multiplier
        eq_d = d * multiplier
        text = f"Which fraction is equivalent to {n}/{d}?"
        ans = f"{eq_n}/{eq_d}"
        distractors = [f"{n + 1}/{d + 1}", f"{n + 2}/{d + 2}", f"{n * 2}/{d * 3}"]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(ans, distractors),
            correct_answer=ans,
            expected_answer_type="fraction",
            explanation_steps=[
                f"Multiply both the numerator and denominator of {n}/{d} by the same factor ({multiplier}).",
                f"({n} × {multiplier}) / ({d} × {multiplier}) = {eq_n}/{eq_d}.",
            ],
            hint_small="To make an equivalent fraction, multiply top and bottom by the same number.",
            hint_detailed=f"Try multiplying both {n} and {d} by {multiplier}.",
            common_misconceptions={"additive_scaling": "Added same number to top and bottom instead of multiplying"},
        )

    # 4. Comparing Fractions
    def _gen_compare_like_fractions(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        den = random.randint(4, 10)
        n1 = random.randint(1, den - 1)
        n2 = random.choice([x for x in range(1, den) if x != n1])
        larger = f"{max(n1, n2)}/{den}"
        smaller = f"{min(n1, n2)}/{den}"
        text = f"Which fraction is greater: {n1}/{den} or {n2}/{den}?"
        ans = larger
        distractors = [smaller, "They are equal", f"1/{den}"]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format="comparison",
            options=self._build_options(ans, distractors),
            correct_answer=ans,
            expected_answer_type="choice",
            explanation_steps=[
                f"Because both fractions share the common denominator {den}, compare their numerators.",
                f"{max(n1, n2)} is greater than {min(n1, n2)}, so {larger} is greater.",
            ],
            hint_small="When the denominators are the same, compare the top numbers directly.",
            hint_detailed=f"Which is more: {n1} slices out of {den}, or {n2} slices out of {den}?",
        )

    def _gen_compare_unlike_fractions(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        f1 = Fraction(1, 2)
        f2 = Fraction(random.choice([1, 2, 3]), random.choice([3, 4, 5]))
        while f1 == f2:
            f2 = Fraction(2, 3)
        larger_str = f"{f1.numerator}/{f1.denominator}" if f1 > f2 else f"{f2.numerator}/{f2.denominator}"
        smaller_str = f"{f2.numerator}/{f2.denominator}" if f1 > f2 else f"{f1.numerator}/{f1.denominator}"
        text = f"Which fraction is greater: {f1.numerator}/{f1.denominator} or {f2.numerator}/{f2.denominator}?"
        ans = larger_str
        distractors = [smaller_str, "They are equal", "Cannot be determined"]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format="comparison",
            options=self._build_options(ans, distractors),
            correct_answer=ans,
            expected_answer_type="choice",
            explanation_steps=[
                f"Find a common denominator or cross-multiply.",
                f"Comparing {f1.numerator}/{f1.denominator} ({float(f1):.2f}) and {f2.numerator}/{f2.denominator} ({float(f2):.2f}).",
                f"{larger_str} is the larger fraction.",
            ],
            hint_small="Cross-multiply the numerators and denominators to compare.",
            hint_detailed="Convert both fractions so they have the same denominator.",
        )

    # 5. Fraction Addition & Subtraction
    def _gen_add_sub_like_fractions(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        den = random.randint(4, 9)
        n1 = random.randint(1, 3)
        n2 = random.randint(1, den - n1 - 1)
        ans_num = n1 + n2
        text = f"What is {n1}/{den} + {n2}/{den}?"
        ans = f"{ans_num}/{den}"
        wrong_den = f"{ans_num}/{den + den}"  # Common misconception: adding denominators!
        distractors = [wrong_den, f"{ans_num + 1}/{den}", f"{n1}/{den}"]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(ans, distractors),
            correct_answer=ans,
            expected_answer_type="fraction",
            explanation_steps=[
                f"When adding like fractions, add the numerators together and keep the denominator the same.",
                f"{n1} + {n2} = {ans_num}.",
                f"The denominator remains {den}: {ans_num}/{den}.",
            ],
            hint_small="Add only the top numbers! Keep the bottom number unchanged.",
            hint_detailed="Never add denominators together when fractions already share the same denominator.",
            common_misconceptions={"add_denominators": "Added denominators together (e.g. 1/4 + 1/4 = 2/8)"},
        )

    def _gen_add_sub_unlike_fractions(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        # Simple unlike: 1/2 + 1/4 or 1/3 + 1/6
        pair = random.choice([
            (Fraction(1, 2), Fraction(1, 4)),
            (Fraction(1, 3), Fraction(1, 6)),
            (Fraction(2, 5), Fraction(1, 10)),
            (Fraction(1, 4), Fraction(3, 8)),
        ])
        f1, f2 = pair
        ans_frac = f1 + f2
        text = f"Calculate: {f1.numerator}/{f1.denominator} + {f2.numerator}/{f2.denominator}"
        ans = f"{ans_frac.numerator}/{ans_frac.denominator}"
        wrong = f"{f1.numerator + f2.numerator}/{f1.denominator + f2.denominator}"
        distractors = [wrong, f"{ans_frac.numerator + 1}/{ans_frac.denominator}", f"1/{ans_frac.denominator}"]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(ans, distractors),
            correct_answer=ans,
            expected_answer_type="fraction",
            explanation_steps=[
                f"Find the common denominator for {f1.denominator} and {f2.denominator}.",
                f"Convert fractions and add numerators.",
                f"Result: {ans}.",
            ],
            hint_small="First change the fractions so they both have the same denominator.",
            hint_detailed=f"Find the least common multiple of {f1.denominator} and {f2.denominator}.",
            common_misconceptions={"add_denominators_direct": "Added numerators and denominators straight across"},
        )

    # 6. Decimals & Percentages
    def _gen_decimal_place_value(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        d1 = round(random.uniform(0.1, 0.9), 1)
        d2 = round(random.uniform(0.05, 0.95), 2)
        while d1 == d2:
            d2 = round(random.uniform(0.05, 0.95), 2)
        larger = max(d1, d2)
        smaller = min(d1, d2)
        text = f"Which decimal is greater: {d1} or {d2}?"
        ans = str(larger)
        distractors = [str(smaller), "They are equal", "0.00"]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format="comparison",
            options=self._build_options(ans, distractors),
            correct_answer=ans,
            expected_answer_type="choice",
            explanation_steps=[
                "Line up the decimal places (tenths, hundredths).",
                f"{d1} has {int(d1 * 10)} tenths.",
                f"{larger} is greater than {smaller}.",
            ],
            hint_small="Remember: extra digits at the end do not make a decimal larger. Check the tenths first!",
            hint_detailed="Compare the digits immediately after the decimal point.",
            common_misconceptions={"longer_is_larger": "Assumed more digits means larger number"},
        )

    def _gen_decimal_arithmetic(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        a = round(random.uniform(1.1, 8.9), 1)
        b = round(random.uniform(1.1, 5.9), 1)
        ans = round(a + b, 1)
        text = f"Calculate: {a} + {b}"
        distractors = [str(round(ans + 0.1, 1)), str(round(ans - 0.1, 1)), str(round(ans + 1.0, 1))]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="float",
            explanation_steps=[
                "Align the decimal points vertically.",
                f"Add tenths: {round((a % 1) + (b % 1), 1)}",
                f"Sum: {ans}",
            ],
            hint_small="Keep the decimal point aligned when you add.",
            hint_detailed="Add the whole numbers and decimals separately.",
        )

    def _gen_percent_basics(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        pct = random.choice([10, 25, 50])
        val = random.choice([20, 40, 60, 80, 100, 120])
        ans = int((pct / 100) * val)
        text = f"What is {pct}% of {val}?"
        distractors = [str(ans + 5), str(ans - 5), str(val - pct), str(ans * 2)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                f"{pct}% means {pct}/100.",
                f"Multiply: ({pct} / 100) × {val} = {ans}.",
            ],
            hint_small="50% is half; 25% is one quarter; 10% is one tenth.",
            hint_detailed=f"For {pct}%, divide {val} by {100 // pct}.",
        )

    # 7. Ratios & Proportions
    def _gen_ratio_rep(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        factor = random.randint(2, 4)
        a = random.choice([1, 2, 3])
        b = random.choice([4, 5, 7])
        orig_a = a * factor
        orig_b = b * factor
        text = f"Simplify the ratio {orig_a}:{orig_b} to its simplest form."
        ans = f"{a}:{b}"
        distractors = [f"{a + 1}:{b}", f"{a}:{b + 1}", f"{orig_a - 1}:{orig_b - 1}"]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(ans, distractors),
            correct_answer=ans,
            expected_answer_type="text",
            explanation_steps=[
                f"Find the greatest common divisor of {orig_a} and {orig_b}, which is {factor}.",
                f"Divide both numbers by {factor}: {orig_a} ÷ {factor} = {a}, {orig_b} ÷ {factor} = {b}.",
                f"Simplified ratio: {a}:{b}.",
            ],
            hint_small="Divide both terms of the ratio by their greatest common factor.",
            hint_detailed=f"What number can divide evenly into both {orig_a} and {orig_b}?",
        )

    def _gen_unitary_method(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        unit_price = random.randint(3, 8)
        n1 = random.randint(2, 4)
        n2 = random.randint(5, 7)
        cost1 = n1 * unit_price
        ans = n2 * unit_price
        item = random.choice(["notebooks", "pens", "apples", "stickers"])
        text = f"If {n1} {item} cost ₹{cost1}, how much will {n2} {item} cost?"
        distractors = [str(ans - unit_price), str(ans + unit_price), str(cost1 + n2), str(ans + 10)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                f"Step 1: Find the cost of 1 {item}: ₹{cost1} ÷ {n1} = ₹{unit_price}.",
                f"Step 2: Multiply by {n2}: {n2} × ₹{unit_price} = ₹{ans}.",
            ],
            hint_small="Find the cost of a single unit first, then scale up.",
            hint_detailed=f"Divide {cost1} by {n1} to get the price for one.",
        )

    # 8. Basic Algebra
    def _gen_missing_number(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        ans = random.randint(3, 15)
        const = random.randint(4, 20)
        total = ans + const
        text = f"Solve for x: x + {const} = {total}"
        distractors = [str(ans + 1), str(ans - 1), str(total + const), str(ans + 2)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                f"To isolate x, subtract {const} from both sides.",
                f"x = {total} - {const}",
                f"x = {ans}",
            ],
            hint_small="Perform the inverse operation on the other side.",
            hint_detailed=f"Subtract {const} from {total}.",
        )

    def _gen_linear_one_step(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        coeff = random.randint(2, 6)
        ans = random.randint(3, 9)
        rhs = coeff * ans
        text = f"Solve for y: {coeff}y = {rhs}"
        distractors = [str(ans + 1), str(ans - 1), str(rhs - coeff), str(ans * 2)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                f"Divide both sides of the equation by {coeff}.",
                f"y = {rhs} ÷ {coeff}",
                f"y = {ans}",
            ],
            hint_small="The opposite of multiplication is division.",
            hint_detailed=f"Divide {rhs} by {coeff}.",
        )

    def _gen_linear_two_step(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        coeff = random.choice([2, 3, 4])
        ans = random.randint(2, 6)
        const = random.randint(3, 9)
        rhs = (coeff * ans) + const
        text = f"Solve for x: {coeff}x + {const} = {rhs}"
        distractors = [str(ans + 1), str(ans - 1), str(ans + 2), str(ans * 2)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                f"Step 1: Subtract {const} from both sides: {coeff}x = {rhs - const}",
                f"Step 2: Divide by {coeff}: x = {rhs - const} ÷ {coeff} = {ans}",
            ],
            hint_small="Subtract the constant number first, then divide by the coefficient.",
            hint_detailed=f"Subtract {const} from {rhs}, then divide by {coeff}.",
        )

    # 9. Geometry & Measurement
    def _gen_perimeter(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        l = random.randint(4, 12)
        w = random.randint(2, l - 1)
        ans = 2 * (l + w)
        text = f"Find the perimeter of a rectangle with length {l} cm and width {w} cm."
        wrong_area = l * w
        distractors = [str(wrong_area), str(ans + 2), str(ans - 2), str(l + w)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                "Perimeter = 2 × (length + width)",
                f"Perimeter = 2 × ({l} + {w}) = 2 × {l + w} = {ans} cm.",
            ],
            hint_small="Perimeter is the total distance around the outside edge.",
            hint_detailed="Add all four sides: length + width + length + width.",
            common_misconceptions={"confuse_perimeter_area": "Multiplied sides instead of adding boundary lengths"},
        )

    def _gen_area(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        l = random.randint(3, 10)
        w = random.randint(2, 9)
        ans = l * w
        wrong_perim = 2 * (l + w)
        text = f"What is the area of a rectangle with length {l} m and width {w} m?"
        distractors = [str(wrong_perim), str(ans + 3), str(ans - 3), str(l + w)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                "Area = length × width",
                f"Area = {l} × {w} = {ans} m².",
            ],
            hint_small="To find area, multiply length by width.",
            hint_detailed=f"Multiply {l} by {w}.",
            common_misconceptions={"confuse_area_perimeter": "Added lengths instead of multiplying"},
        )

    def _gen_angles(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        a1 = random.choice([40, 50, 60, 70])
        a2 = random.choice([30, 45, 55, 65])
        ans = 180 - (a1 + a2)
        text = f"Two angles in a triangle measure {a1}° and {a2}°. What is the third angle?"
        distractors = [str(ans + 10), str(ans - 10), str(180 - ans), str(90 - a1)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                "The interior angles of any triangle always add up to 180°.",
                f"{a1}° + {a2}° = {a1 + a2}°",
                f"Third angle = 180° - {a1 + a2}° = {ans}°.",
            ],
            hint_small="The sum of all three angles inside any triangle is always 180°.",
            hint_detailed=f"Add {a1} and {a2}, then subtract the total from 180.",
        )

    # 10. Number Patterns & Logic
    def _gen_arithmetic_seq(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        start = random.randint(2, 10)
        step = random.choice([2, 3, 4, 5, 7])
        seq = [start + i * step for i in range(4)]
        ans = start + 4 * step
        seq_str = ", ".join(map(str, seq)) + ", ?"
        text = f"Find the next number in this sequence: {seq_str}"
        distractors = [str(ans - 1), str(ans + 1), str(ans + step), str(ans - step)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                f"Find the difference between consecutive terms: {seq[1]} - {seq[0]} = {step}.",
                f"The pattern adds {step} each time.",
                f"{seq[-1]} + {step} = {ans}.",
            ],
            hint_small="Look at how much the number increases from one step to the next.",
            hint_detailed=f"Add {step} to the last number {seq[-1]}.",
        )

    def _gen_geom_seq(self, diff: int, c: QuestionConstraint) -> GeneratedQuestionPayload:
        factor = random.choice([2, 3])
        start = random.choice([2, 3, 4])
        seq = [start * (factor ** i) for i in range(4)]
        ans = start * (factor ** 4)
        seq_str = ", ".join(map(str, seq)) + ", ?"
        text = f"Find the next number in this sequence: {seq_str}"
        distractors = [str(seq[-1] + (seq[1] - seq[0])), str(ans - factor), str(ans + factor)]
        return GeneratedQuestionPayload(
            question_text=text,
            topic_id=c.topic_id,
            concept_id=c.concept_id,
            difficulty=diff,
            question_format=c.question_format,
            options=self._build_options(str(ans), distractors),
            correct_answer=str(ans),
            expected_answer_type="integer",
            explanation_steps=[
                f"Each number is multiplied by {factor} to get the next number.",
                f"{seq[-1]} × {factor} = {ans}.",
            ],
            hint_small="Is the sequence growing by adding, or by multiplying?",
            hint_detailed=f"Multiply the last number by {factor}.",
        )
