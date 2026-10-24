"""Pydantic schemas for curriculum metadata and content updates."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ConceptOverview(BaseModel):
    id: str
    title: str
    difficulty_levels: List[int]
    prerequisites: List[str]
    description: str


class TopicOverview(BaseModel):
    id: str
    title: str
    description: str
    order: int
    concepts: List[ConceptOverview]


class CurriculumOverviewResponse(BaseModel):
    content_version: str
    topics: List[TopicOverview]


class ContentVersionResponse(BaseModel):
    version: str
    released_at: datetime
    description: str
    checksum: str
    is_active: bool
