"""Application configuration using Pydantic Settings."""

import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    PROJECT_NAME: str = "MathQuest Backend"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Environment
    ENV: str = os.getenv("MATHQUEST_ENV", "development")
    DEBUG: bool = os.getenv("MATHQUEST_DEBUG", "false").lower() in ("true", "1", "yes")
    
    # Server
    HOST: str = os.getenv("MATHQUEST_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MATHQUEST_PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv("MATHQUEST_DATABASE_URL", "sqlite:///./mathquest.db")
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("MATHQUEST_RATE_LIMIT_PER_MINUTE", "120"))
    
    # AI Question Generator
    # Supported: "offline", "gemini", "mock"
    AI_PROVIDER: str = os.getenv("MATHQUEST_AI_PROVIDER", "offline")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    AI_TIMEOUT_SECONDS: float = float(os.getenv("MATHQUEST_AI_TIMEOUT_SECONDS", "5.0"))
    AI_MAX_RETRIES: int = int(os.getenv("MATHQUEST_AI_MAX_RETRIES", "2"))
    
    # Firmware and Content updates
    CONTENT_VERSION: str = os.getenv("MATHQUEST_CONTENT_VERSION", "2026.10.1")
    FIRMWARE_CHANNEL: str = os.getenv("MATHQUEST_FIRMWARE_CHANNEL", "stable")
    FIRMWARE_VERSION: str = os.getenv("MATHQUEST_FIRMWARE_VERSION", "1.0.0")


settings = Settings()
