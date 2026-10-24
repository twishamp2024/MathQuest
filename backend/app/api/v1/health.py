"""Health and readiness check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.core.config import settings
from backend.app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check validating application and database connectivity."""
    db_healthy = False
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        db_healthy = False

    return {
        "status": "ok" if db_healthy else "degraded",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
        "database_connected": db_healthy,
        "ai_provider": settings.AI_PROVIDER,
        "content_version": settings.CONTENT_VERSION,
        "firmware_version": settings.FIRMWARE_VERSION,
    }


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe for container and orchestrator deployments."""
    try:
        db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        return {"ready": False}
