"""Learning session management endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import LearnerProfile, LearningSession
from backend.app.core.security import generate_session_id
from backend.app.schemas.session import (
    SessionCreateRequest,
    SessionResponse,
    SessionEndResponse,
)

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def start_session(req: SessionCreateRequest, db: Session = Depends(get_db)):
    """Start a new learning session for an anonymous learner."""
    profile = db.query(LearnerProfile).filter(LearnerProfile.id == req.learner_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found.")

    session_id = generate_session_id()
    session = LearningSession(
        id=session_id,
        learner_id=req.learner_id,
        topic_filter=req.topic_filter,
        game_mode=req.game_mode,
        is_active=True,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Retrieve session status and score metrics."""
    session = db.query(LearningSession).filter(LearningSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session


@router.post("/{session_id}/end", response_model=SessionEndResponse)
def end_session(session_id: str, db: Session = Depends(get_db)):
    """End a learning session and calculate final performance metrics."""
    session = db.query(LearningSession).filter(LearningSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    now = datetime.now(timezone.utc)
    session.ended_at = now
    session.is_active = False
    db.commit()

    # Calculate duration
    duration = (now - session.started_at.replace(tzinfo=timezone.utc)).total_seconds() if session.started_at else 0.0
    acc = (
        round((session.questions_correct / session.questions_attempted) * 100, 1)
        if session.questions_attempted > 0
        else 0.0
    )

    return SessionEndResponse(
        session_id=session.id,
        learner_id=session.learner_id,
        total_questions=session.questions_attempted,
        correct_answers=session.questions_correct,
        accuracy_percentage=acc,
        duration_seconds=round(max(0.0, duration), 1),
    )
