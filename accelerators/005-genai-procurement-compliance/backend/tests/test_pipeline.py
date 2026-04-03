"""Pipeline integration tests — full chat flow."""


def test_chat_compliance_check(client, sample_chat_request):
    response = client.post("/api/chat", json=sample_chat_request)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["confidence"] > 0
    assert isinstance(data["citations"], list)
    assert len(data["citations"]) > 0


def test_chat_gap_analysis(client, sample_gap_request):
    response = client.post("/api/chat", json=sample_gap_request)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "gap" in data["response"].lower() or "issue" in data["response"].lower()


def test_chat_risk_assessment(client, sample_risk_request):
    response = client.post("/api/chat", json=sample_risk_request)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["confidence"] > 0


def test_chat_general_query(client):
    response = client.post("/api/chat", json={"message": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] > 0


def test_chat_regulation_lookup(client):
    response = client.post(
        "/api/chat", json={"message": "What are the EO N-5-26 requirements?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data


def test_chat_missing_message(client):
    response = client.post("/api/chat", json={})
    assert response.status_code == 422


def test_attestation_upload(client):
    response = client.post("/api/attestations")
    assert response.status_code == 200
    data = response.json()
    assert "attestation" in data
    assert data["attestation"]["status"] == "analyzing"


def test_attestation_results(client):
    response = client.get("/api/attestations/ATT-2025-0001/results")
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "results" in data
    assert len(data["results"]) > 0
