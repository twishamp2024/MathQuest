"""Tests for content versioning and firmware OTA architecture."""

def test_content_version_and_checksum(client):
    res = client.get("/api/v1/content/version")
    assert res.status_code == 200
    data = res.json()
    assert "version" in data
    assert "checksum" in data
    assert len(data["checksum"]) == 64  # Valid SHA-256 hex string


def test_curriculum_overview_10_topics(client):
    res = client.get("/api/v1/content/curriculum")
    assert res.status_code == 200
    data = res.json()
    assert len(data["topics"]) == 10
    topic_ids = [t["id"] for t in data["topics"]]
    assert "add_sub" in topic_ids
    assert "mul_div" in topic_ids
    assert "fractions_ops" in topic_ids
    assert "patterns_logic" in topic_ids


def test_firmware_check_update_available(client):
    # Device running older 0.9.0 checks for update
    res = client.post(
        "/api/v1/firmware/check",
        json={
            "current_version": "0.9.0",
            "device_model": "esp32-devkit-v1",
            "channel": "stable",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["update_available"] is True
    assert data["target_version"] == "1.0.0"
    assert data["sha256_hash"] is not None


def test_firmware_check_already_up_to_date(client):
    # Device already running 1.0.0
    res = client.post(
        "/api/v1/firmware/check",
        json={
            "current_version": "1.0.0",
            "device_model": "esp32-devkit-v1",
            "channel": "stable",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["update_available"] is False


def test_firmware_check_incompatible_hardware(client):
    res = client.post(
        "/api/v1/firmware/check",
        json={
            "current_version": "0.8.0",
            "device_model": "arduino-uno-rev3",  # Unsupported board
            "channel": "stable",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["update_available"] is False
    assert "not supported" in data["release_notes"]


def test_firmware_binary_download(client):
    res = client.get("/api/v1/firmware/download/esp32-v1.0.0.bin")
    assert res.status_code == 200
    assert "X-Firmware-SHA256" in res.headers
    assert res.content.startswith(b"\x00\x00\x00\x00MATHQUEST")
