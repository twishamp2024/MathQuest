"""Tests for deterministic adaptive learning engine."""

from backend.app.engine.adaptive import AdaptiveEngine
from backend.app.engine.curriculum import get_concept_by_id
from backend.app.db.models import ConceptMastery


def test_prerequisite_blocks_advanced_concept():
    # If addition is unmastered, multi-digit or fractions should NOT be selected
    mastery_map = {"add_single_digit": 0.20}
    equiv_fractions = get_concept_by_id("equivalent_fractions")
    assert not AdaptiveEngine.are_prerequisites_met(equiv_fractions, mastery_map)

    # If addition and multiplication are mastered, fractions become eligible
    mastery_map_mastered = {
        "add_single_digit": 0.90,
        "sub_single_digit": 0.85,
        "multiplication_facts": 0.88,
        "basic_division": 0.80,
        "fraction_concepts": 0.75,
    }
    assert AdaptiveEngine.are_prerequisites_met(equiv_fractions, mastery_map_mastered)


def test_difficulty_escalates_on_sustained_streak():
    concept = get_concept_by_id("multi_digit_multiplication")
    # Low streak -> baseline difficulty (3)
    diff_baseline, _ = AdaptiveEngine.calculate_difficulty(
        concept=concept,
        current_mastery=0.50,
        consecutive_correct=0,
        consecutive_incorrect=0,
    )
    # Streak of 3 -> difficulty bumped up (4)
    diff_boosted, reason = AdaptiveEngine.calculate_difficulty(
        concept=concept,
        current_mastery=0.50,
        consecutive_correct=3,
        consecutive_incorrect=0,
    )
    assert diff_boosted > diff_baseline
    assert "Sustained streak" in reason


def test_difficulty_lowers_on_repeated_mistakes():
    concept = get_concept_by_id("multi_digit_multiplication")
    diff_normal, _ = AdaptiveEngine.calculate_difficulty(
        concept=concept,
        current_mastery=0.90,
        consecutive_correct=0,
        consecutive_incorrect=0,
    )
    diff_lowered, reason = AdaptiveEngine.calculate_difficulty(
        concept=concept,
        current_mastery=0.90,
        consecutive_correct=0,
        consecutive_incorrect=2,
    )
    assert diff_lowered < diff_normal
    assert "Scaffolding applied" in reason


def test_remedial_redirection_on_failure():
    # When struggling on "add_sub_unlike_fractions", engine should redirect to "add_sub_like_fractions" or "equivalent_fractions"
    mastery_map = {
        "add_single_digit": 0.90,
        "add_sub_like_fractions": 0.55,
        "equivalent_fractions": 0.60,
    }
    concept, is_remedial, parent_id, rationale = AdaptiveEngine.select_next_concept(
        topic_filter=None,
        mastery_map=mastery_map,
        last_concept_id="add_sub_unlike_fractions",
        last_consecutive_incorrect=2,
    )
    assert is_remedial is True
    assert parent_id == "add_sub_unlike_fractions"
    assert concept.id in ("add_sub_like_fractions", "equivalent_fractions")
    assert "Remedial branch triggered" in rationale
