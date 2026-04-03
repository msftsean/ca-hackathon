"""Accuracy evaluation tests for Cross-Agency Knowledge Hub."""

import pytest
from app.pipeline import KnowledgeHubPipeline
from app.models.schemas import ChatRequest


@pytest.fixture
def pipeline():
    return KnowledgeHubPipeline()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message,min_confidence",
    [
        ("Find CDSS policy on CalFresh", 0.7),
        ("Who is the expert on procurement?", 0.7),
        ("Search across all agencies for data governance", 0.5),
        ("Find CalHR telework regulation", 0.7),
        ("What agencies are available?", 0.7),
        ("Hello, help me get started", 0.3),
    ],
)
async def test_confidence_meets_threshold(pipeline, message, min_confidence):
    request = ChatRequest(message=message)
    response = await pipeline.process(request)
    assert response.confidence >= min_confidence, (
        f"Confidence {response.confidence} below threshold {min_confidence} for: {message}"
    )


@pytest.mark.asyncio
async def test_cdss_policy_returns_documents(pipeline):
    request = ChatRequest(message="Find CDSS policy on CalFresh")
    response = await pipeline.process(request)
    assert response.documents is not None
    assert len(response.documents) > 0


@pytest.mark.asyncio
async def test_expert_search_returns_results(pipeline):
    request = ChatRequest(message="Who is the expert on procurement?")
    response = await pipeline.process(request)
    assert response.experts is not None or response.confidence > 0.5


@pytest.mark.asyncio
async def test_all_responses_have_citations(pipeline):
    messages = [
        "Find CDSS policy on CalFresh",
        "Search EDD unemployment procedures",
        "What agencies are available?",
    ]
    for msg in messages:
        request = ChatRequest(message=msg)
        response = await pipeline.process(request)
        assert len(response.citations) > 0, f"No citations for: {msg}"
