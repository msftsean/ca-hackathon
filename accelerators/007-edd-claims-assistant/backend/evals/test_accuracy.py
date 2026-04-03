"""Accuracy evaluation tests for EDD Claims Assistant."""

import pytest
from app.pipeline import EDDClaimsPipeline
from app.models.schemas import ChatRequest


@pytest.fixture
def pipeline():
    return EDDClaimsPipeline()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message,min_confidence",
    [
        ("Check my unemployment claim status", 0.7),
        ("Am I eligible for disability insurance?", 0.7),
        ("How do I file a new unemployment claim?", 0.7),
        ("What documents do I need?", 0.7),
        ("When will I get my payment?", 0.7),
        ("My claim was denied, how do I appeal?", 0.7),
        ("Hello, what can you help with?", 0.3),
    ],
)
async def test_confidence_meets_threshold(pipeline, message, min_confidence):
    request = ChatRequest(message=message)
    response = await pipeline.process(request)
    assert response.confidence >= min_confidence, (
        f"Confidence {response.confidence} below threshold {min_confidence} for: {message}"
    )


@pytest.mark.asyncio
async def test_claim_status_returns_data(pipeline):
    request = ChatRequest(message="Check my unemployment claim status")
    response = await pipeline.process(request)
    assert response.claim_status is not None
    assert response.claim_status.claim_type == "UI"


@pytest.mark.asyncio
async def test_eligibility_returns_assessment(pipeline):
    request = ChatRequest(message="Am I eligible for disability insurance?")
    response = await pipeline.process(request)
    assert response.eligibility is not None
    assert response.eligibility.claim_type == "DI"


@pytest.mark.asyncio
async def test_document_checklist_returned(pipeline):
    request = ChatRequest(message="What documents do I need to upload?")
    response = await pipeline.process(request)
    assert response.document_checklist is not None
    assert len(response.document_checklist) > 0


@pytest.mark.asyncio
async def test_all_responses_have_citations(pipeline):
    messages = [
        "Check my claim status",
        "Am I eligible for UI?",
        "How do I file?",
        "My claim was denied",
    ]
    for msg in messages:
        request = ChatRequest(message=msg)
        response = await pipeline.process(request)
        assert len(response.citations) > 0, f"No citations for: {msg}"
