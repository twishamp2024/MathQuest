"""Tests for EWMA mastery model."""

from backend.app.engine.mastery import MasteryModel


def test_mastery_increases_on_correct_answer():
    result = MasteryModel.update_mastery(
        current_score=0.50,
        current_attempts=2,
        is_correct=True,
        difficulty=3,
        response_time_ms=5000,
        consecutive_correct=0,
        consecutive_incorrect=0,
    )
    assert result.new_score > 0.50
    assert result.score_delta > 0
    assert result.consecutive_correct == 1
    assert result.consecutive_incorrect == 0


def test_mastery_decreases_on_incorrect_answer():
    result = MasteryModel.update_mastery(
        current_score=0.60,
        current_attempts=4,
        is_correct=False,
        difficulty=2,
        response_time_ms=7000,
        consecutive_correct=2,
        consecutive_incorrect=0,
    )
    assert result.new_score < 0.60
    assert result.score_delta < 0
    assert result.consecutive_correct == 0
    assert result.consecutive_incorrect == 1


def test_fluent_speed_bonus():
    # Fast fluent correct vs slow correct
    fast = MasteryModel.update_mastery(
        current_score=0.50,
        current_attempts=1,
        is_correct=True,
        difficulty=2,
        response_time_ms=3000,
        consecutive_correct=0,
        consecutive_incorrect=0,
    )
    slow = MasteryModel.update_mastery(
        current_score=0.50,
        current_attempts=1,
        is_correct=True,
        difficulty=2,
        response_time_ms=30000,
        consecutive_correct=0,
        consecutive_incorrect=0,
    )
    assert fast.new_score > slow.new_score


def test_hysteresis_cushions_isolated_mistake_after_high_mastery():
    # If a mastered learner (0.85) misses one, the drop is moderated
    res = MasteryModel.update_mastery(
        current_score=0.85,
        current_attempts=10,
        is_correct=False,
        difficulty=3,
        response_time_ms=8000,
        consecutive_correct=5,
        consecutive_incorrect=0,
    )
    # Shouldn't plunge below 0.65 on a single mistake
    assert res.new_score >= 0.70


def test_confidence_increases_with_sample_count():
    res1 = MasteryModel.update_mastery(0.5, 0, True, 2, 6000, 0, 0)
    res10 = MasteryModel.update_mastery(0.5, 9, True, 2, 6000, 0, 0)
    assert res10.confidence > res1.confidence
    assert res10.confidence > 0.80
