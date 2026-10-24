"""Content Versioning and Content Update Manager.

Calculates SHA-256 content checksums and manages content bank updates.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any
from backend.app.core.config import settings
from backend.app.engine.curriculum import CURRICULUM
from backend.app.schemas.content import ContentVersionResponse, CurriculumOverviewResponse, TopicOverview, ConceptOverview


class ContentManager:
    """Manages curriculum content versioning and integrity."""

    @classmethod
    def compute_curriculum_checksum(cls) -> str:
        """Compute SHA-256 hash of the complete active curriculum structure."""
        serialized = []
        for tid in sorted(CURRICULUM.keys()):
            topic = CURRICULUM[tid]
            serialized.append({
                "id": topic.id,
                "title": topic.title,
                "concepts": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "diff": c.difficulty_levels,
                        "prereq": sorted(c.prerequisites),
                    }
                    for c in topic.concepts
                ],
            })
        raw_json = json.dumps(serialized, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw_json).hexdigest()

    @classmethod
    def get_current_content_version(cls) -> ContentVersionResponse:
        """Return the current active content version and checksum."""
        checksum = cls.compute_curriculum_checksum()
        return ContentVersionResponse(
            version=settings.CONTENT_VERSION,
            released_at=datetime.now(timezone.utc),
            description="MathQuest 10-Domain Adaptive Primary Curriculum",
            checksum=checksum,
            is_active=True,
        )

    @classmethod
    def get_curriculum_overview(cls) -> CurriculumOverviewResponse:
        """Return structured curriculum metadata."""
        topics_list: list[TopicOverview] = []
        for topic in sorted(CURRICULUM.values(), key=lambda t: t.order):
            concepts_list = [
                ConceptOverview(
                    id=c.id,
                    title=c.title,
                    difficulty_levels=c.difficulty_levels,
                    prerequisites=c.prerequisites,
                    description=c.description,
                )
                for c in topic.concepts
            ]
            topics_list.append(
                TopicOverview(
                    id=topic.id,
                    title=topic.title,
                    description=topic.description,
                    order=topic.order,
                    concepts=concepts_list,
                )
            )
        return CurriculumOverviewResponse(
            content_version=settings.CONTENT_VERSION,
            topics=topics_list,
        )
