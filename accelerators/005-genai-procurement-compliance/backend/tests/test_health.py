"""Health-check endpoint tests."""


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "genai-procurement-compliance"
    assert "mock_mode" in data


def test_status_endpoint(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "genai-procurement-compliance"
    assert "compliance_frameworks" in data
