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
    assert data["service"] == "edd-claims-assistant"
    assert "mock_mode" in data


def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "EDD Claims Assistant"
    assert "supported_claim_types" in data
    assert "UI" in data["supported_claim_types"]


def test_chat_endpoint():
    response = client.post(
        "/api/chat",
        json={"message": "Check my unemployment claim status"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "confidence" in data
    assert "citations" in data
    assert data["confidence"] > 0


def test_chat_with_claim_type():
    response = client.post(
        "/api/chat",
        json={"message": "Am I eligible for disability insurance?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] > 0


def test_claim_status_endpoint():
    response = client.post(
        "/api/claim-status",
        json={"claim_type": "UI", "last_four_ssn": "1234"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claim_type"] == "UI"
    assert "status" in data


def test_eligibility_endpoint():
    response = client.post(
        "/api/eligibility",
        json={"claim_type": "UI"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claim_type"] == "UI"
    assert "likely_eligible" in data
    assert "requirements" in data


def test_document_checklist_endpoint():
    response = client.post(
        "/api/document-checklist",
        json={"claim_type": "UI"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "name" in data[0]
    assert "required" in data[0]
