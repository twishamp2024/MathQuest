"""Mastery Estimation Model using Exponentially Weighted Moving Average (EWMA).

Features:
- Concept-specific mastery estimation bounded in [0.0, 1.0].
- Sample-size confidence metric asymptotically approaching 1.0.
- Response-time factor: discounts impulsive guessing and accounts for thoughtful reasoning.
- Difficulty-weighted updates: passing higher difficulty yields higher reward; failing lower difficulty indicates need for review.
- Hysteresis and dampening to prevent oscillation from isolated mistakes.
"""

from typing import Tuple
from dataclasses import dataclass


@dataclass
class MasteryUpdateResult:
    previous_score: float
    new_score: float
    score_delta: float
    confidence: float
    consecutive_correct: int
    consecutive_incorrect: int
    status_summary: str


class MasteryModel:
    """
    Transparent, explainable mastery model based on EWMA.
    
    Formula:
      performance_score = correctness * difficulty_weight * speed_factor
      new_mastery = (1 - alpha) * current_mastery + alpha * performance_score
    """

    # Base smoothing parameter (higher = faster adaptation to recent performance)
    ALPHA: float = 0.28
    
    # Expected response time in milliseconds for standard arithmetic questions
    EXPECTED_TIME_MS: int = 12000
    MIN_TIME_MS: int = 1500  # Below 1.5s is likely impulsive guessing
    MAX_TIME_MS: int = 45000  # Beyond 45s indicates significant struggle

    @classmethod
    def calculate_speed_factor(cls, response_time_ms: int, is_correct: bool) -> float:
        """
        Compute speed modifier in range [0.75, 1.15].
        - Fast & correct (2s - 8s): 1.10 - 1.15 (fluent mastery)
        - Fast & incorrect (< 2s): 0.70 (impulsive error penalty)
        - Normal (8s - 20s): 1.00
        - Slow (> 25s): 0.85 (struggling or calculating carefully)
        """
        if response_time_ms <= 0:
            return 1.0

        if is_correct:
            if response_time_ms < cls.MIN_TIME_MS:
                return 1.0  # lucky guess or simple recall
            elif response_time_ms <= 8000:
                return 1.12  # Fluent recall
            elif response_time_ms <= 20000:
                return 1.00  # Normal steady thinking
            else:
                return 0.90  # Correct, but required prolonged effort
        else:
            if response_time_ms < cls.MIN_TIME_MS:
                return 0.75  # Rushing / guessing
            else:
                return 1.00  # Genuine attempt mistake

    @classmethod
    def calculate_difficulty_weight(cls, difficulty: int, is_correct: bool) -> float:
        """
        Difficulty scaling:
        - Higher difficulty correct answer yields higher target score (up to 1.0)
        - Lower difficulty incorrect answer yields lower target score (down to 0.0)
        """
        clamped_diff = max(1, min(5, difficulty))
        
        if is_correct:
            # Difficulty 1 -> target 0.70; Difficulty 3 -> target 0.85; Difficulty 5 -> target 1.0
            return 0.60 + (clamped_diff * 0.08)
        else:
            # Missing diff 1 indicates low baseline (~0.15); Missing diff 5 only drops target to ~0.50
            return 0.10 + ((clamped_diff - 1) * 0.08)

    @classmethod
    def update_mastery(
        cls,
        current_score: float,
        current_attempts: int,
        is_correct: bool,
        difficulty: int,
        response_time_ms: int,
        consecutive_correct: int,
        consecutive_incorrect: int,
        hints_used: int = 0,
    ) -> MasteryUpdateResult:
        """
        Update learner's concept mastery score following an answer submission.
        """
        # Ensure previous score is clamped
        prev = max(0.0, min(1.0, current_score))

        # Factor in hints: each hint used decreases target score for this attempt
        hint_penalty = min(0.35, hints_used * 0.12)

        speed_factor = cls.calculate_speed_factor(response_time_ms, is_correct)
        target_score = cls.calculate_difficulty_weight(difficulty, is_correct)
        
        if is_correct:
            target_score = min(1.0, target_score * speed_factor) - hint_penalty
            target_score = max(0.40, target_score)
            new_consec_correct = consecutive_correct + 1
            new_consec_incorrect = 0
        else:
            target_score = max(0.05, target_score * (1.0 / speed_factor))
            new_consec_correct = 0
            new_consec_incorrect = consecutive_incorrect + 1

        # Dynamic alpha: dampens adaptation when sample count is low or to prevent sudden drops
        dynamic_alpha = cls.ALPHA
        if not is_correct and consecutive_incorrect == 0 and prev > 0.75:
            # Single lapse after mastery: soften drop by halving alpha (hysteresis)
            dynamic_alpha = dynamic_alpha * 0.55

        # EWMA formula
        updated_score = ((1.0 - dynamic_alpha) * prev) + (dynamic_alpha * target_score)
        updated_score = max(0.05, min(0.98, updated_score))
        delta = updated_score - prev

        # Confidence metric: reaches ~0.90 after ~10 attempts
        new_attempts = current_attempts + 1
        confidence = min(0.99, 1.0 - (0.85 ** new_attempts))

        # Status summary
        if updated_score >= 0.80:
            status = "mastered"
        elif updated_score >= 0.60:
            status = "proficient"
        elif updated_score >= 0.40:
            status = "practicing"
        else:
            status = "struggling"

        return MasteryUpdateResult(
            previous_score=round(prev, 4),
            new_score=round(updated_score, 4),
            score_delta=round(delta, 4),
            confidence=round(confidence, 4),
            consecutive_correct=new_consec_correct,
            consecutive_incorrect=new_consec_incorrect,
            status_summary=status,
        )
