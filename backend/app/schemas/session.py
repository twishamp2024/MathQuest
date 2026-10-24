"""Pydantic schemas for learning sessions."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SessionCreateRequest(BaseModel):
    learner_id: str
    topic_filter: Optional[str] = None
    game_mode: str = Field(default="adaptive", pattern="^(adaptive|practice|challenge)$")


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    learner_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool
    topic_filter: Optional[str]
    game_mode: str
    questions_attempted: int
    questions_correct: int


class SessionEndResponse(BaseModel):
    session_id: str
    learner_id: str
    total_questions: int
    correct_answers: int
    accuracy_percentage: float
    duration_seconds: float
