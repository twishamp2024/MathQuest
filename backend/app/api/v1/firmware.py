"""ESP32 Firmware OTA metadata and manifest endpoints."""

import os
from fastapi import APIRouter, HTTPException, Response
from backend.app.ota.firmware_manager import FirmwareManager
from backend.app.schemas.firmware import FirmwareCheckRequest, FirmwareManifestResponse

router = APIRouter(prefix="/firmware", tags=["Firmware OTA"])


@router.post("/check", response_model=FirmwareManifestResponse)
def check_firmware_update(req: FirmwareCheckRequest):
    """
    Check if a newer compatible firmware binary is available for an ESP32 hardware device.
    Verifies hardware model, semantic version, and release channel.
    """
    return FirmwareManager.check_update(req)


@router.get("/manifest", response_model=FirmwareManifestResponse)
def get_latest_manifest():
    """Retrieve the manifest for the latest stable ESP32 release."""
    req = FirmwareCheckRequest(current_version="0.0.0", device_model="esp32-devkit-v1", channel="stable")
    return FirmwareManager.check_update(req)


@router.get("/download/{filename}")
def download_firmware_binary(filename: str):
    """
    Serve authorized firmware binary for ESP32 OTA download.
    Includes SHA-256 header for client validation.
    """
    # Safe validation of filename to prevent path traversal
    if not filename.endswith(".bin") or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid firmware binary request.")

    # In development/test mode, provide dummy binary payload with appropriate headers
    dummy_payload = b"\x00\x00\x00\x00MATHQUEST_ESP32_FIRMWARE_V1\x00\x00"
    return Response(
        content=dummy_payload,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Firmware-SHA256": FirmwareManager.LATEST_FIRMWARE["sha256"],
        },
    )
