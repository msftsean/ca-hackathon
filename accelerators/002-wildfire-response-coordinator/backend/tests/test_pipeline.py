"""Tests for WildfirePipeline — end-to-end pipeline integration."""

import pytest
import os
from app.pipeline import WildfirePipeline
from app.models.schemas import ChatRequest


@pytest.fixture
def pipeline():
    os.environ["USE_MOCK_SERVICES"] = "true"
    return WildfirePipeline()


class TestPipelineIntegration:
    @pytest.mark.asyncio
    async def test_incident_flow(self, pipeline):
        request = ChatRequest(message="Report a new fire in Butte County")
        result = await pipeline.process(request)
        assert result.response
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_specific_incident_flow(self, pipeline):
        request = ChatRequest(
            message="What is the status?",
            incident_id="CA-BTU-004521",
        )
        result = await pipeline.process(request)
        assert result.response

    @pytest.mark.asyncio
    async def test_resource_flow(self, pipeline):
        request = ChatRequest(message="We need more engine resources")
        result = await pipeline.process(request)
        assert result.response

    @pytest.mark.asyncio
    async def test_evacuation_flow(self, pipeline):
        request = ChatRequest(message="What are the evacuation zones?")
        result = await pipeline.process(request)
        assert result.response
        assert result.evacuation is not None

    @pytest.mark.asyncio
    async def test_weather_flow(self, pipeline):
        request = ChatRequest(message="What is the weather and humidity?")
        result = await pipeline.process(request)
        assert result.response

    @pytest.mark.asyncio
    async def test_psps_flow(self, pipeline):
        request = ChatRequest(message="Are there any power shutoff events?")
        result = await pipeline.process(request)
        assert result.response

    @pytest.mark.asyncio
    async def test_general_flow(self, pipeline):
        request = ChatRequest(message="How does this system work?")
        result = await pipeline.process(request)
        assert result.response
