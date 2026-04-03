"""Tests for the full pipeline."""

import pytest
from app.models.schemas import ChatRequest
from app.pipeline import BenefitsCalPipeline


@pytest.fixture
def pipeline():
    return BenefitsCalPipeline()


@pytest.mark.asyncio
async def test_pipeline_eligibility(pipeline):
    request = ChatRequest(message="Am I eligible for CalFresh?")
    response = await pipeline.process(request)
    assert response.confidence > 0.5
    assert "CalFresh" in response.response or "calfresh" in response.response.lower()
    assert len(response.citations) > 0


@pytest.mark.asyncio
async def test_pipeline_program_info(pipeline):
    request = ChatRequest(message="What is CalWORKs? Tell me about it")
    response = await pipeline.process(request)
    assert response.confidence > 0.5
    assert len(response.citations) > 0


@pytest.mark.asyncio
async def test_pipeline_application_help(pipeline):
    request = ChatRequest(message="How do I apply for CalFresh?")
    response = await pipeline.process(request)
    assert response.confidence > 0.5
    assert "apply" in response.response.lower() or "application" in response.response.lower()


@pytest.mark.asyncio
async def test_pipeline_document_requirements(pipeline):
    request = ChatRequest(message="What documents do I need for CalWORKs?")
    response = await pipeline.process(request)
    assert response.confidence > 0.5
    assert "document" in response.response.lower() or "proof" in response.response.lower()


@pytest.mark.asyncio
async def test_pipeline_office_locations(pipeline):
    request = ChatRequest(message="Where is the nearest office in Los Angeles?")
    response = await pipeline.process(request)
    assert response.confidence > 0.5
    assert "Los Angeles" in response.response


@pytest.mark.asyncio
async def test_pipeline_general_query(pipeline):
    request = ChatRequest(message="I need help")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert len(response.citations) > 0


@pytest.mark.asyncio
async def test_pipeline_returns_citations(pipeline):
    request = ChatRequest(message="Am I eligible for CalFresh?")
    response = await pipeline.process(request)
    assert len(response.citations) > 0
    for citation in response.citations:
        assert citation.source != ""


@pytest.mark.asyncio
async def test_pipeline_with_county(pipeline):
    request = ChatRequest(
        message="Where is the nearest office?",
        county="Sacramento",
    )
    response = await pipeline.process(request)
    assert response.confidence > 0
