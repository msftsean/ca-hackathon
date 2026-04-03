"""Tests for the full pipeline."""

import pytest
from app.models.schemas import ChatRequest
from app.pipeline import PermitPipeline


@pytest.fixture
def pipeline():
    return PermitPipeline()


@pytest.mark.asyncio
async def test_pipeline_project_intake(pipeline):
    request = ChatRequest(message="I want to build an addition to my house")
    response = await pipeline.process(request)
    assert response.confidence > 0.5
    assert len(response.citations) > 0


@pytest.mark.asyncio
async def test_pipeline_requirement_check(pipeline):
    request = ChatRequest(message="What documents do I need for a renovation permit?")
    response = await pipeline.process(request)
    assert response.confidence > 0.5
    assert "document" in response.response.lower() or "need" in response.response.lower()


@pytest.mark.asyncio
async def test_pipeline_zoning_check(pipeline):
    request = ChatRequest(message="What is the zoning for 123 Main St?")
    response = await pipeline.process(request)
    assert response.confidence > 0.5
    assert "zone" in response.response.lower() or "zoning" in response.response.lower()


@pytest.mark.asyncio
async def test_pipeline_status_check(pipeline):
    request = ChatRequest(message="What is the status of my application?")
    response = await pipeline.process(request)
    assert response.confidence > 0.5


@pytest.mark.asyncio
async def test_pipeline_fee_estimate(pipeline):
    request = ChatRequest(message="How much does a building permit cost?")
    response = await pipeline.process(request)
    assert response.confidence > 0.5
    assert "$" in response.response or "fee" in response.response.lower()


@pytest.mark.asyncio
async def test_pipeline_general_query(pipeline):
    request = ChatRequest(message="I have a question about permits")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert len(response.citations) > 0


@pytest.mark.asyncio
async def test_pipeline_returns_citations(pipeline):
    request = ChatRequest(message="I want to build a new house")
    response = await pipeline.process(request)
    assert len(response.citations) > 0
    for citation in response.citations:
        assert citation.source != ""


@pytest.mark.asyncio
async def test_pipeline_adu_project(pipeline):
    request = ChatRequest(message="I want to build an ADU in my backyard")
    response = await pipeline.process(request)
    assert response.confidence > 0.5
