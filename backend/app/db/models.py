"""SQLAlchemy Database Models for MathQuest.

Features:
- Completely anonymous learner profiles (no PII: no name, email, phone, location)
- Learning sessions and question history
- Granular concept mastery records with EWMA tracking
- Question & answer records with response time and detected misconceptions
- Content bank versions & firmware release manifests
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


def utcnow() -> datetime:
    """Current UTC datetime."""
    return datetime.now(timezone.utc)


class LearnerProfile(Base):
    """Anonymous learner profile."""
    __tablename__ = "learner_profiles"

    id = Column(String(64), primary_key=True, index=True)
    display_alias = Column(String(64), nullable=False, default="Math Explorer")
    avatar_icon = Column(String(32), nullable=False, default="rocket")
    created_at = Column(DateTime, default=utcnow, nullable=False)
    last_active_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    
    # Cumulative stats
    total_questions_answered = Column(Integer, default=0, nullable=False)
    total_correct = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    highest_streak = Column(Integer, default=0, nullable=False)

    # Relationships
    sessions = relationship("LearningSession", back_populates="learner", cascade="all, delete-orphan")
    mastery_records = relationship("ConceptMastery", back_populates="learner", cascade="all, delete-orphan")
    questions = relationship("QuestionLog", back_populates="learner", cascade="all, delete-orphan")
    answers = relationship("AnswerRecord", back_populates="learner", cascade="all, delete-orphan")


class LearningSession(Base):
    """Learning session record."""
    __tablename__ = "learning_sessions"

    id = Column(String(64), primary_key=True, index=True)
    learner_id = Column(String(64), ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime, default=utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    topic_filter = Column(String(64), nullable=True)  # None or specific topic id
    game_mode = Column(String(32), default="adaptive", nullable=False)  # adaptive, practice, challenge
    questions_attempted = Column(Integer, default=0, nullable=False)
    questions_correct = Column(Integer, default=0, nullable=False)

    # Relationships
    learner = relationship("LearnerProfile", back_populates="sessions")
    questions = relationship("QuestionLog", back_populates="session")


class ConceptMastery(Base):
    """
    Granular concept mastery tracking per learner.
    Mastery score is modeled as an EWMA (Exponentially Weighted Moving Average)
    between 0.0 (novice) and 1.0 (mastered).
    """
    __tablename__ = "concept_mastery"

    id = Column(Integer, primary_key=True, autoincrement=True)
    learner_id = Column(String(64), ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(64), nullable=False, index=True)
    concept_id = Column(String(64), nullable=False, index=True)
    
    mastery_score = Column(Float, default=0.5, nullable=False)  # Starting baseline 0.5
    confidence = Column(Float, default=0.1, nullable=False)     # Increases with sample count (0.0 - 1.0)
    attempts_count = Column(Integer, default=0, nullable=False)
    correct_count = Column(Integer, default=0, nullable=False)
    consecutive_correct = Column(Integer, default=0, nullable=False)
    consecutive_incorrect = Column(Integer, default=0, nullable=False)
    last_attempt_at = Column(DateTime, default=utcnow, nullable=False)

    learner = relationship("LearnerProfile", back_populates="mastery_records")

    __table_args__ = (
        UniqueConstraint("learner_id", "concept_id", name="uq_learner_concept"),
        Index("idx_learner_topic", "learner_id", "topic_id"),
    )


class QuestionLog(Base):
    """Historical log of questions presented to learners."""
    __tablename__ = "question_logs"

    id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("learning_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    learner_id = Column(String(64), ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    topic_id = Column(String(64), nullable=False)
    concept_id = Column(String(64), nullable=False)
    difficulty = Column(Integer, default=1, nullable=False)  # 1 to 5
    
    question_text = Column(Text, nullable=False)
    question_format = Column(String(32), default="multiple_choice", nullable=False)  # multiple_choice, numeric, comparison
    options_json = Column(Text, nullable=True)  # JSON serialized list of options if applicable
    correct_answer = Column(String(128), nullable=False)
    
    generator_source = Column(String(32), default="offline", nullable=False)  # offline, gemini, bank
    recommendation_reason = Column(Text, nullable=True)  # Explainable decision audit trail
    
    created_at = Column(DateTime, default=utcnow, nullable=False)

    learner = relationship("LearnerProfile", back_populates="questions")
    session = relationship("LearningSession", back_populates="questions")
    answers = relationship("AnswerRecord", back_populates="question")


class AnswerRecord(Base):
    """Record of learner answers, response times, and detected misconceptions."""
    __tablename__ = "answer_records"

    id = Column(String(64), primary_key=True, index=True)
    question_id = Column(String(64), ForeignKey("question_logs.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(64), nullable=True, index=True)
    learner_id = Column(String(64), ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    submitted_answer = Column(String(128), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    response_time_ms = Column(Integer, default=0, nullable=False)
    hints_requested = Column(Integer, default=0, nullable=False)
    detected_misconception = Column(String(128), nullable=True)
    
    created_at = Column(DateTime, default=utcnow, nullable=False)

    learner = relationship("LearnerProfile", back_populates="answers")
    question = relationship("QuestionLog", back_populates="answers")


class ContentVersion(Base):
    """Curriculum content versions."""
    __tablename__ = "content_versions"

    version = Column(String(32), primary_key=True)
    released_at = Column(DateTime, default=utcnow, nullable=False)
    description = Column(String(255), nullable=False)
    checksum = Column(String(64), nullable=False)  # SHA-256 of question bank & curriculum
    is_active = Column(Boolean, default=True, nullable=False)


class FirmwareManifest(Base):
    """ESP32 Firmware OTA releases and update manifests."""
    __tablename__ = "firmware_manifests"

    version = Column(String(32), primary_key=True)
    channel = Column(String(32), default="stable", nullable=False)
    min_hardware_version = Column(String(32), default="esp32-v1", nullable=False)
    binary_url = Column(String(255), nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    signature = Column(Text, nullable=True)
    release_notes = Column(Text, nullable=True)
    is_critical = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime, default=utcnow, nullable=False)
