"""Pydantic schemas for anonymous learner profiles and mastery."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ConceptMasterySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    topic_id: str
    concept_id: str
    mastery_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    attempts_count: int
    correct_count: int
    consecutive_correct: int
    consecutive_incorrect: int
    last_attempt_at: datetime


class LearnerCreateRequest(BaseModel):
    display_alias: Optional[str] = Field(default=None, max_length=64)
    avatar_icon: Optional[str] = Field(default="rocket", max_length=32)


class LearnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    display_alias: str
    avatar_icon: str
    created_at: datetime
    last_active_at: datetime
    total_questions_answered: int
    total_correct: int
    current_streak: int
    highest_streak: int
    mastery_records: List[ConceptMasterySchema] = []


class LearnerStatsResponse(BaseModel):
    learner_id: str
    display_alias: str
    total_questions_answered: int
    total_correct: int
    accuracy_percentage: float
    current_streak: int
    highest_streak: int
    active_topics_count: int
    mastery_by_topic: dict[str, float]
