"""Tests for ActionAgent — response generation across all modules."""

import pytest
import os
from app.agents.action_agent import ActionAgent
from app.models.schemas import IncidentQuery, RoutingDecision


@pytest.fixture
def agent():
    os.environ["USE_MOCK_SERVICES"] = "true"
    return ActionAgent()


class TestIncidentCommand:
    @pytest.mark.asyncio
    async def test_specific_incident(self, agent):
        query = IncidentQuery(
            raw_input="Status of CA-BTU-004521",
            intent="incident_report",
            entities={"incident_id": "CA-BTU-004521"},
        )
        routing = RoutingDecision(destination="incident_command")
        result = await agent.execute(query, routing)
        assert result.incident is not None
        assert "Paradise Ridge" in result.response
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_all_incidents(self, agent):
        query = IncidentQuery(raw_input="Show all incidents", intent="incident_report")
        routing = RoutingDecision(destination="incident_command")
        result = await agent.execute(query, routing)
        assert "Active" in result.response
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_incident_citations(self, agent):
        query = IncidentQuery(raw_input="Incident status", intent="incident_report")
        routing = RoutingDecision(destination="incident_command")
        result = await agent.execute(query, routing)
        assert len(result.citations) > 0


class TestResourceManagement:
    @pytest.mark.asyncio
    async def test_available_resources(self, agent):
        query = IncidentQuery(raw_input="What resources are available?", intent="resource_request")
        routing = RoutingDecision(destination="resource_management")
        result = await agent.execute(query, routing)
        assert result.resources is not None
        assert len(result.resources) > 0

    @pytest.mark.asyncio
    async def test_specific_resource_type(self, agent):
        query = IncidentQuery(
            raw_input="Need helicopters",
            intent="resource_request",
            entities={"resource_types": ["helicopter"]},
        )
        routing = RoutingDecision(destination="resource_management")
        result = await agent.execute(query, routing)
        assert result.response


class TestEvacuationOps:
    @pytest.mark.asyncio
    async def test_evacuation_info(self, agent):
        query = IncidentQuery(raw_input="Evacuation zones", intent="evacuation_query")
        routing = RoutingDecision(destination="evacuation_ops")
        result = await agent.execute(query, routing)
        assert result.evacuation is not None
        assert len(result.evacuation.zones) > 0
        assert result.evacuation.total_evacuated > 0

    @pytest.mark.asyncio
    async def test_evacuation_citations(self, agent):
        query = IncidentQuery(raw_input="Evacuation status", intent="evacuation_query")
        routing = RoutingDecision(destination="evacuation_ops")
        result = await agent.execute(query, routing)
        assert len(result.citations) > 0


class TestWeatherOps:
    @pytest.mark.asyncio
    async def test_weather_all(self, agent):
        query = IncidentQuery(raw_input="Weather briefing", intent="weather_check")
        routing = RoutingDecision(destination="weather_ops")
        result = await agent.execute(query, routing)
        assert "Weather" in result.response or "weather" in result.response.lower()
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_weather_specific_county(self, agent):
        query = IncidentQuery(
            raw_input="Weather in Butte County",
            intent="weather_check",
            entities={"county": "Butte"},
        )
        routing = RoutingDecision(destination="weather_ops")
        result = await agent.execute(query, routing)
        assert "Butte" in result.response


class TestUtilityCoordination:
    @pytest.mark.asyncio
    async def test_psps_events(self, agent):
        query = IncidentQuery(raw_input="PSPS events", intent="psps_info")
        routing = RoutingDecision(destination="utility_coordination")
        result = await agent.execute(query, routing)
        assert "Power Shutoff" in result.response or "PGE" in result.response


class TestInteragency:
    @pytest.mark.asyncio
    async def test_agency_coordination(self, agent):
        query = IncidentQuery(raw_input="Agency contacts", intent="agency_coordination")
        routing = RoutingDecision(destination="interagency")
        result = await agent.execute(query, routing)
        assert "CAL_FIRE" in result.response or "Agency" in result.response

    @pytest.mark.asyncio
    async def test_general_response(self, agent):
        query = IncidentQuery(raw_input="Help", intent="general_info")
        routing = RoutingDecision(destination="unknown")
        result = await agent.execute(query, routing)
        assert result.response
