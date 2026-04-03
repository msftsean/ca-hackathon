"""Tests for QueryAgent — intent detection and entity extraction."""

import pytest
from app.agents.query_agent import QueryAgent


@pytest.fixture
def agent():
    return QueryAgent()


class TestIntentDetection:
    @pytest.mark.asyncio
    async def test_incident_report(self, agent):
        result = await agent.process("There is a new fire in Butte County")
        assert result.intent == "incident_report"

    @pytest.mark.asyncio
    async def test_resource_request(self, agent):
        result = await agent.process("We need more engine resources deployed")
        assert result.intent == "resource_request"

    @pytest.mark.asyncio
    async def test_evacuation_query(self, agent):
        result = await agent.process("What are the current evacuation zones?")
        assert result.intent == "evacuation_query"

    @pytest.mark.asyncio
    async def test_weather_check(self, agent):
        result = await agent.process("What is the current weather and humidity?")
        assert result.intent == "weather_check"

    @pytest.mark.asyncio
    async def test_psps_info(self, agent):
        result = await agent.process("Are there any power shutoff events?")
        assert result.intent == "psps_info"

    @pytest.mark.asyncio
    async def test_agency_coordination(self, agent):
        result = await agent.process("Need to coordinate mutual aid with adjacent agencies")
        assert result.intent == "agency_coordination"

    @pytest.mark.asyncio
    async def test_status_update(self, agent):
        result = await agent.process("What is the containment status update?")
        assert result.intent == "status_update"

    @pytest.mark.asyncio
    async def test_general_info(self, agent):
        result = await agent.process("How does this system work?")
        assert result.intent == "general_info"


class TestEntityExtraction:
    @pytest.mark.asyncio
    async def test_extract_county(self, agent):
        result = await agent.process("Report fire in Los Angeles county area")
        assert result.entities.get("county") == "Los Angeles"

    @pytest.mark.asyncio
    async def test_extract_resource_types(self, agent):
        result = await agent.process("We need helicopter and dozer support")
        assert "helicopter" in result.entities.get("resource_types", [])
        assert "dozer" in result.entities.get("resource_types", [])

    @pytest.mark.asyncio
    async def test_extract_incident_id(self, agent):
        result = await agent.process("Status of incident CA-BTU-004521")
        assert result.entities.get("incident_id") == "CA-BTU-004521"

    @pytest.mark.asyncio
    async def test_extract_acreage(self, agent):
        result = await agent.process("Fire has burned 500 acres")
        assert result.entities.get("acres") == 500.0

    @pytest.mark.asyncio
    async def test_extract_containment(self, agent):
        result = await agent.process("Fire is 25% contained")
        assert result.entities.get("containment_pct") == 25.0


class TestIncidentTypeDetection:
    @pytest.mark.asyncio
    async def test_detect_wildfire(self, agent):
        result = await agent.process("Report a wildfire in the forest")
        assert result.incident_type == "wildfire"

    @pytest.mark.asyncio
    async def test_detect_structure_fire(self, agent):
        result = await agent.process("There is a structure fire in downtown")
        assert result.incident_type == "structure_fire"

    @pytest.mark.asyncio
    async def test_detect_flood(self, agent):
        result = await agent.process("Flash flood warning issued")
        assert result.incident_type == "flood"

    @pytest.mark.asyncio
    async def test_no_incident_type(self, agent):
        result = await agent.process("What is the status?")
        assert result.incident_type is None
