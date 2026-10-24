"""Tests for health and readiness endpoints."""

def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database_connected"] is True
    assert "version" in data
    assert "content_version" in data


def test_readiness_probe(client):
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True
