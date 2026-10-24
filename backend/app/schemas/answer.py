"""Pydantic schemas for answer submissions, hints, and explanations."""

from typing import Optional, List
from pydantic import BaseModel, Field


class AnswerSubmitRequest(BaseModel):
    learner_id: str
    question_id: str
    session_id: Optional[str] = None
    submitted_answer: str = Field(min_length=1, max_length=128)
    response_time_ms: int = Field(ge=0, default=0)
    hints_used: int = Field(ge=0, default=0)


class AnswerSubmitResponse(BaseModel):
    is_correct: bool
    submitted_answer: str
    correct_answer: str
    feedback_message: str
    detected_misconception: Optional[str] = None
    explanation: Optional[str] = None
    explanation_steps: List[str] = []
    current_streak: int
    highest_streak: int
    mastery_change: float
    new_mastery_score: float
    concept_id: str


class HintRequest(BaseModel):
    learner_id: str
    question_id: str
    hint_level: int = Field(ge=1, le=3, default=1)  # 1: conceptual prompt, 2: detailed guidance, 3: worked example


class HintResponse(BaseModel):
    question_id: str
    hint_level: int
    hint_text: str
    step_by_step: Optional[List[str]] = None
    worked_example: Optional[str] = None
