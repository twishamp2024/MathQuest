"""Anonymous learner profile management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.db.session import get_db
from backend.app.db.models import LearnerProfile, ConceptMastery, AnswerRecord
from backend.app.core.security import generate_learner_id, validate_learner_id
from backend.app.schemas.learner import (
    LearnerCreateRequest,
    LearnerResponse,
    LearnerStatsResponse,
    ConceptMasterySchema,
)

router = APIRouter(prefix="/learners", tags=["Learners"])


@router.post("", response_model=LearnerResponse, status_code=status.HTTP_201_CREATED)
def create_learner_profile(req: LearnerCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new anonymous learner profile.
    No personal identifiable information (name, email, age) is collected.
    """
    learner_id = generate_learner_id()
    alias = req.display_alias or f"Explorer {learner_id[-4:].upper()}"
    avatar = req.avatar_icon or "rocket"

    profile = LearnerProfile(
        id=learner_id,
        display_alias=alias,
        avatar_icon=avatar,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{learner_id}", response_model=LearnerResponse)
def get_learner_profile(learner_id: str, db: Session = Depends(get_db)):
    """Retrieve an anonymous learner profile and concept mastery records."""
    if not validate_learner_id(learner_id):
        raise HTTPException(status_code=400, detail="Invalid learner ID format.")

    profile = db.query(LearnerProfile).filter(LearnerProfile.id == learner_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found.")

    return profile


@router.get("/{learner_id}/stats", response_model=LearnerStatsResponse)
def get_learner_stats(learner_id: str, db: Session = Depends(get_db)):
    """Retrieve performance statistics and topic mastery breakdown."""
    if not validate_learner_id(learner_id):
        raise HTTPException(status_code=400, detail="Invalid learner ID format.")

    profile = db.query(LearnerProfile).filter(LearnerProfile.id == learner_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found.")

    mastery_records = db.query(ConceptMastery).filter(ConceptMastery.learner_id == learner_id).all()
    
    # Calculate average mastery grouped by topic
    topic_scores: dict[str, list[float]] = {}
    for m in mastery_records:
        topic_scores.setdefault(m.topic_id, []).append(m.mastery_score)

    mastery_by_topic = {
        topic: round(sum(scores) / len(scores), 2)
        for topic, scores in topic_scores.items()
    }

    acc = (
        round((profile.total_correct / profile.total_questions_answered) * 100, 1)
        if profile.total_questions_answered > 0
        else 0.0
    )

    return LearnerStatsResponse(
        learner_id=profile.id,
        display_alias=profile.display_alias,
        total_questions_answered=profile.total_questions_answered,
        total_correct=profile.total_correct,
        accuracy_percentage=acc,
        current_streak=profile.current_streak,
        highest_streak=profile.highest_streak,
        active_topics_count=len(mastery_by_topic),
        mastery_by_topic=mastery_by_topic,
    )
