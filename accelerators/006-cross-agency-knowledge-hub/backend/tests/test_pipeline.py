"""Pipeline integration tests."""

import pytest
from app.pipeline import KnowledgeHubPipeline
from app.models.schemas import ChatRequest


@pytest.fixture
def pipeline():
    return KnowledgeHubPipeline()


@pytest.mark.asyncio
async def test_pipeline_policy_search(pipeline):
    request = ChatRequest(message="Find CDSS policy on CalFresh")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert len(response.citations) > 0
    assert response.response


@pytest.mark.asyncio
async def test_pipeline_expert_search(pipeline):
    request = ChatRequest(message="Who is the expert on procurement?")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert response.response


@pytest.mark.asyncio
async def test_pipeline_cross_reference(pipeline):
    request = ChatRequest(message="What documents are related to or cross-reference data governance?")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert response.response


@pytest.mark.asyncio
async def test_pipeline_agency_filter(pipeline):
    request = ChatRequest(
        message="Search for policies",
        agency_filter=["DHCS"],
    )
    response = await pipeline.process(request)
    assert response.confidence > 0
    if response.documents:
        for doc in response.documents:
            assert doc.agency == "DHCS"


@pytest.mark.asyncio
async def test_pipeline_general_query(pipeline):
    request = ChatRequest(message="Hello, what can you help with?")
    response = await pipeline.process(request)
    assert response.confidence > 0
    assert response.response
