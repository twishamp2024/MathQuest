"""Curriculum content metadata and versioning endpoints."""

from fastapi import APIRouter
from backend.app.ota.content_manager import ContentManager
from backend.app.schemas.content import ContentVersionResponse, CurriculumOverviewResponse

router = APIRouter(prefix="/content", tags=["Content"])


@router.get("/version", response_model=ContentVersionResponse)
def get_content_version():
    """Retrieve the current active curriculum content version and SHA-256 integrity hash."""
    return ContentManager.get_current_content_version()


@router.get("/curriculum", response_model=CurriculumOverviewResponse)
def get_curriculum_overview():
    """Retrieve the full 10-topic curriculum, concepts, and prerequisite graph."""
    return ContentManager.get_curriculum_overview()
