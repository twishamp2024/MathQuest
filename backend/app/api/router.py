"""API V1 Router Aggregation."""

from fastapi import APIRouter
from backend.app.api.v1 import (
    health,
    learners,
    sessions,
    questions,
    content,
    firmware,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(learners.router)
api_router.include_router(sessions.router)
api_router.include_router(questions.router)
api_router.include_router(content.router)
api_router.include_router(firmware.router)
