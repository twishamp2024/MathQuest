"""Adaptive question generation, answer submission, and hint endpoints."""

import json
import secrets
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import (
    LearnerProfile,
    LearningSession,
    ConceptMastery,
    QuestionLog,
    AnswerRecord,
)
from backend.app.engine.adaptive import AdaptiveEngine
from backend.app.engine.curriculum import get_concept_by_id, get_topic_by_id
from backend.app.engine.mastery import MasteryModel
from backend.app.generators.ai_generator import AIQuestionGenerator
from backend.app.validators.math_validator import MathValidator
from backend.app.remediation.misconceptions import MisconceptionDetector
from backend.app.remediation.hint_engine import HintEngine
from backend.app.schemas.question import QuestionResponse
from backend.app.schemas.answer import (
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    HintRequest,
    HintResponse,
)

router = APIRouter(prefix="/questions", tags=["Questions"])

# Generator instance
question_generator = AIQuestionGenerator()


@router.get("/next", response_model=QuestionResponse)
def get_next_question(
    learner_id: str = Query(..., description="Anonymous learner identifier"),
    session_id: Optional[str] = Query(None, description="Optional active session identifier"),
    topic_filter: Optional[str] = Query(None, description="Optional topic ID to focus on"),
    db: Session = Depends(get_db),
):
    """
    Fetch the next adaptively selected question tailored to the learner's profile.
    Decisions are fully deterministic and explainable.
    """
    profile = db.query(LearnerProfile).filter(LearnerProfile.id == learner_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found.")

    # Fetch mastery records
    mastery_records = (
        db.query(ConceptMastery)
        .filter(ConceptMastery.learner_id == learner_id)
        .all()
    )

    # Fetch last 15 questions to avoid repeats
    recent_logs = (
        db.query(QuestionLog)
        .filter(QuestionLog.learner_id == learner_id)
        .order_by(QuestionLog.created_at.desc())
        .limit(15)
        .all()
    )
    recent_texts = [q.question_text for q in recent_logs]

    # Find last question answered for streak/remedial context
    last_q = recent_logs[0] if recent_logs else None
    last_concept_id = last_q.concept_id if last_q else None
    consec_correct = 0
    consec_incorrect = 0

    if last_concept_id:
        last_mastery = (
            db.query(ConceptMastery)
            .filter(
                ConceptMastery.learner_id == learner_id,
                ConceptMastery.concept_id == last_concept_id,
            )
            .first()
        )
        if last_mastery:
            consec_correct = last_mastery.consecutive_correct
            consec_incorrect = last_mastery.consecutive_incorrect

    # Consult Adaptive Engine
    rec = AdaptiveEngine.recommend_next_question(
        learner_id=learner_id,
        topic_filter=topic_filter,
        mastery_records=mastery_records,
        recent_question_texts=recent_texts,
        last_concept_id=last_concept_id,
        last_consecutive_correct=consec_correct,
        last_consecutive_incorrect=consec_incorrect,
    )

    # Generate question payload
    payload, source = question_generator.generate(rec.constraints)

    # Persist question log with correct answer
    question_id = f"q_{secrets.token_hex(8)}"
    q_log = QuestionLog(
        id=question_id,
        session_id=session_id,
        learner_id=learner_id,
        topic_id=payload.topic_id,
        concept_id=payload.concept_id,
        difficulty=payload.difficulty,
        question_text=payload.question_text,
        question_format=payload.question_format,
        options_json=json.dumps(payload.options) if payload.options else None,
        correct_answer=payload.correct_answer,
        generator_source=source,
        recommendation_reason=rec.rationale,
    )
    db.add(q_log)
    db.commit()

    # Omit correct_answer from child-facing client response!
    return QuestionResponse(
        question_id=question_id,
        session_id=session_id,
        topic_id=payload.topic_id,
        topic_title=rec.topic_title,
        concept_id=payload.concept_id,
        concept_title=rec.concept_title,
        difficulty=payload.difficulty,
        question_text=payload.question_text,
        question_format=payload.question_format,
        options=payload.options,
        has_small_hint=bool(payload.hint_small),
        has_detailed_hint=bool(payload.hint_detailed),
        recommendation_reason=rec.rationale,
        created_at=q_log.created_at,
    )


@router.post("/answer", response_model=AnswerSubmitResponse)
def submit_answer(req: AnswerSubmitRequest, db: Session = Depends(get_db)):
    """
    Submit an answer, evaluate correctness, update concept mastery via EWMA,
    detect misconceptions, and return instant feedback.
    """
    profile = db.query(LearnerProfile).filter(LearnerProfile.id == req.learner_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found.")

    q_log = db.query(QuestionLog).filter(QuestionLog.id == req.question_id).first()
    if not q_log:
        raise HTTPException(status_code=404, detail="Question not found.")

    # 1. Mathematical Validation of Answer
    is_correct = MathValidator.are_answers_equivalent(
        submitted=req.submitted_answer,
        expected=q_log.correct_answer,
        answer_type=q_log.question_format,
    )

    # 2. Misconception Detection if incorrect
    detected_misconception = None
    if not is_correct:
        detected_misconception = MisconceptionDetector.analyze(
            concept_id=q_log.concept_id,
            question_text=q_log.question_text,
            submitted=req.submitted_answer,
            correct_answer=q_log.correct_answer,
        )

    # 3. Retrieve or initialize ConceptMastery
    mastery = (
        db.query(ConceptMastery)
        .filter(
            ConceptMastery.learner_id == req.learner_id,
            ConceptMastery.concept_id == q_log.concept_id,
        )
        .first()
    )
    if not mastery:
        mastery = ConceptMastery(
            learner_id=req.learner_id,
            topic_id=q_log.topic_id,
            concept_id=q_log.concept_id,
            mastery_score=0.50,
            confidence=0.10,
            attempts_count=0,
            correct_count=0,
            consecutive_correct=0,
            consecutive_incorrect=0,
        )
        db.add(mastery)

    # 4. Update Mastery using EWMA model
    res = MasteryModel.update_mastery(
        current_score=mastery.mastery_score,
        current_attempts=mastery.attempts_count,
        is_correct=is_correct,
        difficulty=q_log.difficulty,
        response_time_ms=req.response_time_ms,
        consecutive_correct=mastery.consecutive_correct,
        consecutive_incorrect=mastery.consecutive_incorrect,
        hints_used=req.hints_used,
    )

    mastery.mastery_score = res.new_score
    mastery.confidence = res.confidence
    mastery.attempts_count += 1
    if is_correct:
        mastery.correct_count += 1
    mastery.consecutive_correct = res.consecutive_correct
    mastery.consecutive_incorrect = res.consecutive_incorrect

    # 5. Update Profile Stats & Streak
    profile.total_questions_answered += 1
    if is_correct:
        profile.total_correct += 1
        profile.current_streak += 1
        if profile.current_streak > profile.highest_streak:
            profile.highest_streak = profile.current_streak
    else:
        profile.current_streak = 0

    # 6. Update Session Stats if applicable
    if req.session_id:
        sess = db.query(LearningSession).filter(LearningSession.id == req.session_id).first()
        if sess:
            sess.questions_attempted += 1
            if is_correct:
                sess.questions_correct += 1

    # 7. Persist Answer Record
    ans_record = AnswerRecord(
        id=f"ans_{secrets.token_hex(8)}",
        question_id=req.question_id,
        session_id=req.session_id,
        learner_id=req.learner_id,
        submitted_answer=req.submitted_answer,
        is_correct=is_correct,
        response_time_ms=req.response_time_ms,
        hints_requested=req.hints_used,
        detected_misconception=detected_misconception,
    )
    db.add(ans_record)
    db.commit()

    # Formulate feedback message
    if is_correct:
        msg = f"Awesome job! That is correct!"
        if profile.current_streak >= 3:
            msg += f" Streak: {profile.current_streak} in a row!"
    else:
        msg = f"Not quite. The correct answer was {q_log.correct_answer}."
        if detected_misconception:
            msg += f" Tip: {detected_misconception}"

    return AnswerSubmitResponse(
        is_correct=is_correct,
        submitted_answer=req.submitted_answer,
        correct_answer=q_log.correct_answer,
        feedback_message=msg,
        detected_misconception=detected_misconception,
        explanation=None,
        explanation_steps=[f"Correct answer is {q_log.correct_answer}"],
        current_streak=profile.current_streak,
        highest_streak=profile.highest_streak,
        mastery_change=res.score_delta,
        new_mastery_score=res.new_score,
        concept_id=q_log.concept_id,
    )


@router.post("/hint", response_model=HintResponse)
def get_question_hint(req: HintRequest, db: Session = Depends(get_db)):
    """Request a progressive hint (level 1=prompt, 2=steps, 3=worked example)."""
    q_log = db.query(QuestionLog).filter(QuestionLog.id == req.question_id).first()
    if not q_log:
        raise HTTPException(status_code=404, detail="Question not found.")

    concept = get_concept_by_id(q_log.concept_id)
    hint_small = "Think carefully about the arithmetic relationship."
    hint_detailed = f"Focus on concept: {concept.title if concept else 'Math fact'}."
    if concept and concept.common_misconceptions:
        hint_detailed = list(concept.common_misconceptions.values())[0]

    return HintEngine.get_hint(
        question_id=req.question_id,
        hint_level=req.hint_level,
        hint_small=hint_small,
        hint_detailed=hint_detailed,
        explanation_steps=[f"Solve for {q_log.question_text}", f"Result is {q_log.correct_answer}"],
        correct_answer=q_log.correct_answer,
    )
