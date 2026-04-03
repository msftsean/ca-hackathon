"""Accuracy evaluation tests for Permit Streamliner."""

import json
import pathlib
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.agents.query_agent import QueryAgent

EVAL_CONFIG = pathlib.Path(__file__).parent / "eval_config.json"
client = TestClient(app)
query_agent = QueryAgent()


def load_test_cases():
    with open(EVAL_CONFIG) as f:
        config = json.load(f)
    return config["test_cases"]


TEST_CASES = load_test_cases()


@pytest.mark.parametrize("case", TEST_CASES, ids=[c["id"] for c in TEST_CASES])
@pytest.mark.asyncio
async def test_intent_detection(case):
    query = await query_agent.process(case["input"])
    assert query.intent == case["expected_intent"], (
        f"Expected intent '{case['expected_intent']}' but got '{query.intent}' "
        f"for input: {case['input']}"
    )


@pytest.mark.parametrize("case", TEST_CASES, ids=[c["id"] for c in TEST_CASES])
def test_chat_confidence(case):
    response = client.post("/api/chat", json={"message": case["input"]})
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] >= case["expected_min_confidence"], (
        f"Expected confidence >= {case['expected_min_confidence']} "
        f"but got {data['confidence']} for input: {case['input']}"
    )
