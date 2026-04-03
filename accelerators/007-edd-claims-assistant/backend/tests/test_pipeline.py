"""Pipeline integration tests."""

import pytest
from app.pipeline import EDDClaimsPipeline
from app.models.schemas import ChatRequest


@pytest.fixture
def pipeline():
    return EDDClaimsPipeline()


@pytest.mark.asyncio
async def test_pipeline_claim_status(pipeline):
    request = ChatRequest(message="Check my unemployment claim status")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert len(response.citations) > 0
    assert response.response
    assert response.claim_status is not None


@pytest.mark.asyncio
async def test_pipeline_eligibility(pipeline):
    request = ChatRequest(message="Am I eligible for disability insurance?")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert response.response
    assert response.eligibility is not None


@pytest.mark.asyncio
async def test_pipeline_filing_help(pipeline):
    request = ChatRequest(message="How do I file a new unemployment claim?")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert response.response


@pytest.mark.asyncio
async def test_pipeline_document_requirements(pipeline):
    request = ChatRequest(message="What documents do I need to upload for my claim?")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert response.response
    assert response.document_checklist is not None


@pytest.mark.asyncio
async def test_pipeline_appeal(pipeline):
    request = ChatRequest(message="My claim was denied, how do I appeal?")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert response.response
    assert any("appeal" in c.text.lower() or "appeal" in c.source.lower() for c in response.citations)


@pytest.mark.asyncio
async def test_pipeline_general(pipeline):
    request = ChatRequest(message="Hello, what can you help with?")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert response.response
