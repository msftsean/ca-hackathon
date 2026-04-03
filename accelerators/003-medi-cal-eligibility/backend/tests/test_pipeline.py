"""Tests for MediCalPipeline — end-to-end pipeline integration."""

import pytest
import os
from app.pipeline import MediCalPipeline
from app.models.schemas import ChatRequest


@pytest.fixture
def pipeline():
    os.environ["USE_MOCK_SERVICES"] = "true"
    return MediCalPipeline()


class TestPipelineIntegration:
    @pytest.mark.asyncio
    async def test_eligibility_flow(self, pipeline):
        request = ChatRequest(message="I make $1,500 per month, am I eligible for Medi-Cal?")
        result = await pipeline.process(request)
        assert result.response
        assert result.confidence > 0
        assert result.eligibility is not None
        assert result.eligibility.likely_eligible is True

    @pytest.mark.asyncio
    async def test_general_query(self, pipeline):
        request = ChatRequest(message="What programs are available?")
        result = await pipeline.process(request)
        assert result.response
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_application_status_flow(self, pipeline):
        request = ChatRequest(
            message="What is my application status?",
            application_id="MC-2025-00001",
        )
        result = await pipeline.process(request)
        assert result.response
        assert result.application is not None

    @pytest.mark.asyncio
    async def test_document_help_flow(self, pipeline):
        request = ChatRequest(message="What documents do I need to submit?")
        result = await pipeline.process(request)
        assert result.response
        assert "document" in result.response.lower()

    @pytest.mark.asyncio
    async def test_county_info_flow(self, pipeline):
        request = ChatRequest(message="Where is the county office in Los Angeles?")
        result = await pipeline.process(request)
        assert result.response

    @pytest.mark.asyncio
    async def test_income_query_with_amount(self, pipeline):
        request = ChatRequest(message="I earn $3,500 per month in wages")
        result = await pipeline.process(request)
        assert result.response
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_pregnancy_escalation(self, pipeline):
        request = ChatRequest(message="I'm pregnant and need Medi-Cal coverage")
        result = await pipeline.process(request)
        assert result.response
