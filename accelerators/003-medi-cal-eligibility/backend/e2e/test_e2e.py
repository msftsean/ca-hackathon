"""End-to-end tests for Medi-Cal Eligibility Agent API."""

import pytest
import os
from fastapi.testclient import TestClient

os.environ["USE_MOCK_SERVICES"] = "true"
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "medi-cal-eligibility"


class TestStatusEndpoint:
    def test_status(self):
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "medi-cal-eligibility"
        assert "agents" in data
        assert "supported_programs" in data


class TestChatEndpoint:
    def test_eligibility_query(self):
        response = client.post("/api/chat", json={
            "message": "I make $1,500 per month. Am I eligible for Medi-Cal?"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"]
        assert data["confidence"] > 0
        assert data["eligibility"] is not None
        assert data["eligibility"]["likely_eligible"] is True

    def test_general_query(self):
        response = client.post("/api/chat", json={
            "message": "What is Medi-Cal?"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"]

    def test_application_status_query(self):
        response = client.post("/api/chat", json={
            "message": "Check my application",
            "application_id": "MC-2025-00001"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["application"] is not None

    def test_spanish_language(self):
        response = client.post("/api/chat", json={
            "message": "Soy elegible para Medi-Cal?",
            "language": "es"
        })
        assert response.status_code == 200


class TestEligibilityScreenEndpoint:
    def test_screen_eligible(self):
        response = client.post("/api/eligibility/screen", json={
            "monthly_income": 1000.0,
            "household_size": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert data["likely_eligible"] is True
        assert data["program_type"] == "MAGI_Adult"

    def test_screen_ineligible(self):
        response = client.post("/api/eligibility/screen", json={
            "monthly_income": 5000.0,
            "household_size": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert data["likely_eligible"] is False

    def test_screen_child_program(self):
        response = client.post("/api/eligibility/screen", json={
            "monthly_income": 2500.0,
            "household_size": 2,
            "program_type": "MAGI_Child"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["program_type"] == "MAGI_Child"


class TestApplicationEndpoints:
    def test_create_application(self):
        response = client.post("/api/applications", json={
            "applicant_name": "Test User",
            "household_size": 2,
            "monthly_income": 1800.0,
            "county": "Sacramento"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["app_id"].startswith("MC-2025-")
        assert data["status"] == "draft"

    def test_get_application(self):
        response = client.get("/api/applications/MC-2025-00001")
        assert response.status_code == 200
        data = response.json()
        assert data["app_id"] == "MC-2025-00001"

    def test_get_unknown_application(self):
        response = client.get("/api/applications/MC-9999-99999")
        assert response.status_code == 404
