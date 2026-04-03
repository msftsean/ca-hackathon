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
    assert data["service"] == "cross-agency-knowledge-hub"
    assert "mock_mode" in data


def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Cross-Agency Knowledge Hub"
    assert "mock_mode" in data
    assert "cross_references_enabled" in data


def test_chat_endpoint():
    response = client.post(
        "/api/chat",
        json={"message": "Find CDSS policy on CalFresh"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "confidence" in data
    assert "citations" in data
    assert data["confidence"] > 0


def test_chat_with_agency_filter():
    response = client.post(
        "/api/chat",
        json={
            "message": "Search for policies",
            "agency_filter": ["CDSS"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] > 0


def test_search_endpoint():
    response = client.get("/api/search?query=policy")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data


def test_document_endpoint():
    response = client.get("/api/documents/POL-CDSS-2024-001")
    assert response.status_code == 200
