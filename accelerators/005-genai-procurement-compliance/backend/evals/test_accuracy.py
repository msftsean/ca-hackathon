"""Accuracy evaluation — runs eval_config test cases through /api/chat."""

import json
from pathlib import Path

import pytest

EVAL_CONFIG = Path(__file__).parent / "eval_config.json"


def _load_cases():
    with open(EVAL_CONFIG) as f:
        return json.load(f)["test_cases"]


TEST_CASES = _load_cases()


@pytest.mark.anyio
@pytest.mark.parametrize("case", TEST_CASES, ids=[c["id"] for c in TEST_CASES])
async def test_accuracy(async_client, case):
    payload = {"message": case["message"]}
    resp = await async_client.post("/api/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["confidence"] >= case["min_confidence"], (
        f"Confidence {data['confidence']} < {case['min_confidence']} for {case['id']}"
    )
    assert len(data["response"]) > 0
