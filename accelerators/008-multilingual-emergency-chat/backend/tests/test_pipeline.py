"""Pipeline integration tests — full chat flow."""


def test_chat_wildfire_alerts(client, sample_chat_request):
    response = client.post("/api/chat", json=sample_chat_request)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["language"] == "en"
    assert data["confidence"] > 0
    assert isinstance(data["citations"], list)
    assert len(data["citations"]) > 0


def test_chat_shelter_search(client, sample_shelter_request):
    response = client.post("/api/chat", json=sample_shelter_request)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["confidence"] > 0


def test_chat_air_quality(client, sample_aqi_request):
    response = client.post("/api/chat", json=sample_aqi_request)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "air" in data["response"].lower() or "aqi" in data["response"].lower()


def test_chat_general_query(client):
    response = client.post("/api/chat", json={"message": "hello", "language": "en"})
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] > 0


def test_chat_with_spanish(client):
    response = client.post(
        "/api/chat",
        json={"message": "Are there any alerts?", "language": "es"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "es"


def test_chat_missing_message(client):
    response = client.post("/api/chat", json={"language": "en"})
    assert response.status_code == 422
