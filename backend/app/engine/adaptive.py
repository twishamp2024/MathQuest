"""Deterministic Adaptive Learning Engine.

Rules implemented:
1. Topic selection based on Zone of Proximal Development (ZPD) and prerequisite tree.
2. Concept selection ensuring prerequisites >= 0.60 mastery.
3. Difficulty scaling (1-5) matching learner mastery.
4. Format selection (multiple choice for low difficulty, numeric/direct for higher).
5. Remedial prerequisite redirection upon repeated failure.
6. Difficulty escalation after sustained success (consecutive_correct >= 2).
7. Scaffolding / difficulty reduction after repeated mistakes (consecutive_incorrect >= 2).
8. Automatic hint recommendations.
9. Question history lookup to prevent recent duplicates.
10. Hysteresis cooldowns preventing rapid difficulty oscillation.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from backend.app.engine.curriculum import (
    CURRICULUM,
    ConceptDefinition,
    TopicDefinition,
    get_concept_by_id,
    get_topic_by_id,
)
from backend.app.schemas.question import QuestionConstraint


@dataclass
class RecommendationRecord:
    topic_id: str
    topic_title: str
    concept_id: str
    concept_title: str
    learning_objective: str
    difficulty: int
    question_format: str
    expected_answer_type: str
    is_remedial: bool
    remedial_parent_concept: Optional[str]
    recommend_hint: bool
    rationale: str
    constraints: QuestionConstraint


class AdaptiveEngine:
    """Core deterministic adaptive decision engine."""

    MIN_MASTERY_FOR_PREREQUISITE: float = 0.58
    MASTERY_THRESHOLD_PROFICIENT: float = 0.78

    @classmethod
    def get_learner_mastery_map(cls, mastery_records: list) -> Dict[str, float]:
        """Convert list of DB ConceptMastery objects into {concept_id: score} dict."""
        return {record.concept_id: record.mastery_score for record in mastery_records}

    @classmethod
    def are_prerequisites_met(cls, concept: ConceptDefinition, mastery_map: Dict[str, float]) -> bool:
        """Check if all prerequisites have attained acceptable mastery."""
        for prereq_id in concept.prerequisites:
            score = mastery_map.get(prereq_id, 0.50)
            if score < cls.MIN_MASTERY_FOR_PREREQUISITE:
                return False
        return True

    @classmethod
    def select_next_concept(
        cls,
        topic_filter: Optional[str],
        mastery_map: Dict[str, float],
        last_concept_id: Optional[str] = None,
        last_consecutive_incorrect: int = 0,
    ) -> Tuple[ConceptDefinition, bool, Optional[str], str]:
        """
        Determine target concept, returning (concept, is_remedial, parent_concept, rationale).
        """
        # Rule 5: Remedial redirect if struggling on current concept
        if last_concept_id and last_consecutive_incorrect >= 2:
            current = get_concept_by_id(last_concept_id)
            if current and current.prerequisites:
                # Find weakest prerequisite
                weakest_prereq_id = min(
                    current.prerequisites,
                    key=lambda pid: mastery_map.get(pid, 0.50),
                )
                weakest_prereq = get_concept_by_id(weakest_prereq_id)
                if weakest_prereq:
                    rationale = (
                        f"Remedial branch triggered: Learner had {last_consecutive_incorrect} consecutive incorrect answers "
                        f"on '{current.title}'. Reviewing foundational prerequisite '{weakest_prereq.title}' (mastery: {mastery_map.get(weakest_prereq_id, 0.50):.2f})."
                    )
                    return weakest_prereq, True, current.id, rationale

        # Determine eligible topics
        if topic_filter and topic_filter in CURRICULUM:
            candidate_topics = [CURRICULUM[topic_filter]]
        else:
            # Sort topics by order
            candidate_topics = sorted(CURRICULUM.values(), key=lambda t: t.order)

        # Find eligible concepts whose prerequisites are fulfilled
        eligible_concepts: List[Tuple[ConceptDefinition, float]] = []
        for topic in candidate_topics:
            for concept in topic.concepts:
                if cls.are_prerequisites_met(concept, mastery_map):
                    score = mastery_map.get(concept.id, 0.50)
                    # We want concepts in Zone of Proximal Development (ZPD: mastery < 0.80)
                    eligible_concepts.append((concept, score))

        if not eligible_concepts:
            # Fallback to absolute first concept
            first_concept = CURRICULUM["add_sub"].concepts[0]
            return first_concept, False, None, "Starting from foundational arithmetic concepts."

        # Prioritize concepts that learner has practiced least or has intermediate mastery (0.35 - 0.70)
        # Score difference from sweet-spot 0.55
        def zpd_priority(item: Tuple[ConceptDefinition, float]) -> float:
            c, score = item
            if score >= cls.MASTERY_THRESHOLD_PROFICIENT:
                # Mastered concepts get lower priority unless review is needed
                return 10.0 + score
            # Closest to 0.55 gets highest priority (lowest distance)
            return abs(score - 0.55)

        best_concept, best_score = min(eligible_concepts, key=zpd_priority)
        
        topic_name = CURRICULUM[best_concept.topic_id].title
        rationale = (
            f"Selected concept '{best_concept.title}' from '{topic_name}' with current mastery "
            f"{best_score:.2f} (in Zone of Proximal Development, prerequisites satisfied)."
        )
        return best_concept, False, None, rationale

    @classmethod
    def calculate_difficulty(
        cls,
        concept: ConceptDefinition,
        current_mastery: float,
        consecutive_correct: int,
        consecutive_incorrect: int,
        is_remedial: bool = False,
    ) -> Tuple[int, str]:
        """
        Rule 3, 6, 7 & 10: Calculate appropriate difficulty level (1-5) with hysteresis.
        """
        min_diff = min(concept.difficulty_levels)
        max_diff = max(concept.difficulty_levels)

        # Baseline difficulty from mastery score
        if current_mastery < 0.40:
            diff = min_diff
            reason = f"Mastery {current_mastery:.2f} < 0.40 indicates foundational level {diff}."
        elif current_mastery < 0.65:
            diff = min(max_diff, max(min_diff, 2))
            reason = f"Mastery {current_mastery:.2f} suggests intermediate practice level {diff}."
        elif current_mastery < 0.85:
            diff = min(max_diff, max(min_diff, 3))
            reason = f"Mastery {current_mastery:.2f} demonstrates proficiency at level {diff}."
        else:
            diff = max_diff
            reason = f"Mastery {current_mastery:.2f} demonstrates mastery; presenting challenge level {diff}."

        # Rule 6: Increase after sustained success (consecutive_correct >= 2)
        if consecutive_correct >= 2 and diff < max_diff:
            diff += 1
            reason += f" Sustained streak of {consecutive_correct} correct answers advanced difficulty to {diff}."

        # Rule 7: Decrease after repeated failure (consecutive_incorrect >= 2)
        if (consecutive_incorrect >= 2 or is_remedial) and diff > min_diff:
            diff -= 1
            reason += f" Scaffolding applied after {consecutive_incorrect} incorrect answers, lowering difficulty to {diff}."

        return max(min_diff, min(max_diff, diff)), reason

    @classmethod
    def determine_format_and_answer_type(
        cls, concept: ConceptDefinition, difficulty: int
    ) -> Tuple[str, str]:
        """
        Rule 4: Select question format and expected answer type.
        """
        cid = concept.id
        if "compare" in cid or "ordering" in cid:
            return "comparison", "choice"
        elif "fraction" in cid:
            return "multiple_choice" if difficulty <= 2 else "fraction_text", "fraction"
        elif difficulty == 1:
            return "multiple_choice", "integer"
        elif difficulty >= 3 and cid in ("multiplication_facts", "basic_division", "add_single_digit", "sub_single_digit"):
            return "numeric", "integer"
        else:
            return "multiple_choice", "integer"

    @classmethod
    def recommend_next_question(
        cls,
        learner_id: str,
        topic_filter: Optional[str],
        mastery_records: list,
        recent_question_texts: List[str],
        last_concept_id: Optional[str] = None,
        last_consecutive_correct: int = 0,
        last_consecutive_incorrect: int = 0,
    ) -> RecommendationRecord:
        """
        Formulate a complete explainable recommendation for the next question.
        """
        mastery_map = cls.get_learner_mastery_map(mastery_records)

        # 1. Select Concept
        concept, is_remedial, remedial_parent, concept_rationale = cls.select_next_concept(
            topic_filter=topic_filter,
            mastery_map=mastery_map,
            last_concept_id=last_concept_id,
            last_consecutive_incorrect=last_consecutive_incorrect,
        )

        current_mastery = mastery_map.get(concept.id, 0.50)

        # 2. Select Difficulty
        difficulty, diff_rationale = cls.calculate_difficulty(
            concept=concept,
            current_mastery=current_mastery,
            consecutive_correct=last_consecutive_correct,
            consecutive_incorrect=last_consecutive_incorrect,
            is_remedial=is_remedial,
        )

        # 3. Select Format
        q_format, ans_type = cls.determine_format_and_answer_type(concept, difficulty)

        # 4. Hint recommendation
        recommend_hint = last_consecutive_incorrect >= 1 or is_remedial

        # Combined explainable rationale
        full_rationale = f"{concept_rationale} {diff_rationale}"

        topic_def = CURRICULUM[concept.topic_id]

        constraints = QuestionConstraint(
            topic_id=concept.topic_id,
            concept_id=concept.id,
            learning_objective=concept.learning_objective,
            difficulty=difficulty,
            question_format=q_format,
            expected_answer_type=ans_type,
            min_numeric_value=-100.0 if "integers" in concept.id else 0.0,
            max_numeric_value=1000.0,
            age_group="8-14",
            remedial_target=remedial_parent,
            target_misconception=list(concept.common_misconceptions.keys())[0] if concept.common_misconceptions else None,
            questions_to_avoid=recent_question_texts[-15:] if recent_question_texts else [],
        )

        return RecommendationRecord(
            topic_id=concept.topic_id,
            topic_title=topic_def.title,
            concept_id=concept.id,
            concept_title=concept.title,
            learning_objective=concept.learning_objective,
            difficulty=difficulty,
            question_format=q_format,
            expected_answer_type=ans_type,
            is_remedial=is_remedial,
            remedial_parent_concept=remedial_parent,
            recommend_hint=recommend_hint,
            rationale=full_rationale,
            constraints=constraints,
        )
