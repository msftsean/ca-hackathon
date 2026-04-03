"""Health check and API endpoint tests."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "permit-streamliner"
    assert "mock_mode" in data


def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Permit Streamliner"
    assert "supported_permit_types" in data


def test_applications_endpoint():
    response = client.get("/api/applications")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert data[0]["app_id"].startswith("PRM-")


def test_zoning_check_endpoint():
    response = client.get("/api/zoning/check?address=123+Main+St")
    assert response.status_code == 200
    data = response.json()
    assert "zone_code" in data
    assert "permitted_uses" in data


def test_chat_endpoint():
    response = client.post(
        "/api/chat",
        json={"message": "I want to build an addition"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "confidence" in data
    assert data["confidence"] > 0


def test_chat_zoning():
    response = client.post(
        "/api/chat",
        json={"message": "What is the zoning for 123 Main St?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] > 0


def test_chat_fee_estimate():
    response = client.post(
        "/api/chat",
        json={"message": "How much does a residential permit cost?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
