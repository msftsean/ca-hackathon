"""End-to-end tests for Wildfire Response Coordinator API."""

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
        assert data["service"] == "wildfire-response-coordinator"


class TestStatusEndpoint:
    def test_status(self):
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "wildfire-response-coordinator"
        assert "agents" in data
        assert "capabilities" in data


class TestChatEndpoint:
    def test_incident_query(self):
        response = client.post("/api/chat", json={
            "message": "Report a new fire in Butte County"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"]
        assert data["confidence"] > 0

    def test_resource_query(self):
        response = client.post("/api/chat", json={
            "message": "We need more engine resources deployed"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"]

    def test_evacuation_query(self):
        response = client.post("/api/chat", json={
            "message": "What are the current evacuation zones?"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["evacuation"] is not None

    def test_weather_query(self):
        response = client.post("/api/chat", json={
            "message": "What is the weather and humidity?"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"]

    def test_with_incident_id(self):
        response = client.post("/api/chat", json={
            "message": "What is the status?",
            "incident_id": "CA-BTU-004521"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["incident"] is not None


class TestIncidentEndpoints:
    def test_list_incidents(self):
        response = client.get("/api/incidents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_get_incident(self):
        response = client.get("/api/incidents/CA-BTU-004521")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Paradise Ridge Fire"

    def test_get_unknown_incident(self):
        response = client.get("/api/incidents/CA-XXX-999999")
        assert response.status_code == 404

    def test_create_incident(self):
        response = client.post("/api/incidents", json={
            "name": "Test Fire",
            "incident_type": "wildfire",
            "severity": "minor",
            "location": "Test Location",
            "county": "Test County"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["incident_id"].startswith("CA-NEW-")
        assert data["status"] == "active"


class TestResourceEndpoints:
    def test_available_resources(self):
        response = client.get("/api/resources/available")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0


class TestWeatherEndpoint:
    def test_all_weather(self):
        response = client.get("/api/weather")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_weather_by_county(self):
        response = client.get("/api/weather?county=Butte")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["red_flag_warning"] is True
