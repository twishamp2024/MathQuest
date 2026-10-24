"""Tests for student misconception detection and structured hints."""

from backend.app.remediation.misconceptions import MisconceptionDetector
from backend.app.remediation.hint_engine import HintEngine


def test_detect_adding_denominators_misconception():
    explanation = MisconceptionDetector.analyze(
        concept_id="add_sub_like_fractions",
        question_text="What is 1/4 + 2/4?",
        submitted="3/8",  # 1+2 / 4+4
        correct_answer="3/4",
    )
    assert explanation is not None
    assert "added the denominators" in explanation


def test_detect_pemdas_order_misconception():
    explanation = MisconceptionDetector.analyze(
        concept_id="order_of_operations",
        question_text="Evaluate: 3 + 4 * 5",
        submitted="35",  # (3+4)*5
        correct_answer="23",
    )
    assert explanation is not None
    assert "added before multiplying" in explanation


def test_detect_perimeter_area_confusion():
    explanation = MisconceptionDetector.analyze(
        concept_id="perimeter_calculation",
        question_text="Find the perimeter of a rectangle with length 6 cm and width 4 cm.",
        submitted="24",  # 6 * 4 instead of 2 * (6 + 4) = 20
        correct_answer="20",
    )
    assert explanation is not None
    assert "multiplied the sides" in explanation


def test_hint_engine_progressive_levels():
    steps = ["Step 1: Start with 6", "Step 2: Add 7", "Step 3: Result is 13"]
    # Level 1: Gentle prompt
    h1 = HintEngine.get_hint("q_1", 1, "Count on from 7", "Detailed step", steps, "13")
    assert h1.hint_level == 1
    assert "Count on" in h1.hint_text
    assert h1.worked_example is None

    # Level 2: Strategic guidance
    h2 = HintEngine.get_hint("q_1", 2, "Count on from 7", "Detailed step", steps, "13")
    assert h2.hint_level == 2
    assert h2.step_by_step is not None

    # Level 3: Full worked example
    h3 = HintEngine.get_hint("q_1", 3, "Count on from 7", "Detailed step", steps, "13")
    assert h3.hint_level == 3
    assert h3.worked_example is not None
