"""Pydantic schemas for firmware OTA checks and manifests."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FirmwareCheckRequest(BaseModel):
    current_version: str = Field(min_length=1, max_length=32)
    device_model: str = Field(default="esp32-devkit-v1", max_length=64)
    channel: str = Field(default="stable", pattern="^(stable|beta|dev)$")


class FirmwareManifestResponse(BaseModel):
    update_available: bool
    current_version: str
    target_version: Optional[str] = None
    binary_url: Optional[str] = None
    sha256_hash: Optional[str] = None
    signature: Optional[str] = None
    is_critical: bool = False
    release_notes: Optional[str] = None
    published_at: Optional[datetime] = None
