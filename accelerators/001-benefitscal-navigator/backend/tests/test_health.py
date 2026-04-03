"""Health check and API endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "benefitscal-navigator"
    assert "mock_mode" in data


def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "BenefitsCal Navigator"
    assert "supported_languages" in data
    assert "en" in data["supported_languages"]


def test_programs_endpoint():
    response = client.get("/api/programs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    names = [p["name"] for p in data]
    assert "CalFresh" in names
    assert "CalWORKs" in names


def test_chat_endpoint():
    response = client.post(
        "/api/chat",
        json={"message": "Am I eligible for CalFresh?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "confidence" in data
    assert "citations" in data
    assert data["confidence"] > 0


def test_chat_with_language():
    response = client.post(
        "/api/chat",
        json={"message": "Tell me about CalWORKs", "language": "es"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] > 0


def test_chat_with_county():
    response = client.post(
        "/api/chat",
        json={
            "message": "Where is the nearest office?",
            "county": "San Diego",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
