"""Tests for RouterAgent — routing, priority, and escalation."""

import pytest
from app.agents.router_agent import RouterAgent
from app.models.schemas import IncidentQuery


@pytest.fixture
def router():
    return RouterAgent()


class TestRouting:
    @pytest.mark.asyncio
    async def test_incident_route(self, router):
        query = IncidentQuery(raw_input="New fire", intent="incident_report")
        result = await router.route(query)
        assert result.destination == "incident_command"

    @pytest.mark.asyncio
    async def test_resource_route(self, router):
        query = IncidentQuery(raw_input="Need resources", intent="resource_request")
        result = await router.route(query)
        assert result.destination == "resource_management"

    @pytest.mark.asyncio
    async def test_evacuation_route(self, router):
        query = IncidentQuery(raw_input="Evacuation zones", intent="evacuation_query")
        result = await router.route(query)
        assert result.destination == "evacuation_ops"

    @pytest.mark.asyncio
    async def test_weather_route(self, router):
        query = IncidentQuery(raw_input="Weather info", intent="weather_check")
        result = await router.route(query)
        assert result.destination == "weather_ops"

    @pytest.mark.asyncio
    async def test_psps_route(self, router):
        query = IncidentQuery(raw_input="Power shutoff", intent="psps_info")
        result = await router.route(query)
        assert result.destination == "utility_coordination"

    @pytest.mark.asyncio
    async def test_agency_route(self, router):
        query = IncidentQuery(raw_input="Contact agency", intent="agency_coordination")
        result = await router.route(query)
        assert result.destination == "interagency"

    @pytest.mark.asyncio
    async def test_default_route(self, router):
        query = IncidentQuery(raw_input="Hello", intent="unknown")
        result = await router.route(query)
        assert result.destination == "incident_command"


class TestPriority:
    @pytest.mark.asyncio
    async def test_incident_critical(self, router):
        query = IncidentQuery(raw_input="New fire", intent="incident_report")
        result = await router.route(query)
        assert result.priority == "critical"

    @pytest.mark.asyncio
    async def test_evacuation_critical(self, router):
        query = IncidentQuery(raw_input="Evacuate", intent="evacuation_query")
        result = await router.route(query)
        assert result.priority == "critical"

    @pytest.mark.asyncio
    async def test_resource_high(self, router):
        query = IncidentQuery(raw_input="Resources", intent="resource_request")
        result = await router.route(query)
        assert result.priority == "high"

    @pytest.mark.asyncio
    async def test_weather_medium(self, router):
        query = IncidentQuery(raw_input="Weather", intent="weather_check")
        result = await router.route(query)
        assert result.priority == "medium"

    @pytest.mark.asyncio
    async def test_general_low(self, router):
        query = IncidentQuery(raw_input="Info", intent="general_info")
        result = await router.route(query)
        assert result.priority == "low"


class TestEscalation:
    @pytest.mark.asyncio
    async def test_catastrophic_escalation(self, router):
        query = IncidentQuery(raw_input="Catastrophic fire spreading rapidly", intent="incident_report")
        result = await router.route(query)
        assert result.escalate is True
        assert result.priority == "critical"

    @pytest.mark.asyncio
    async def test_low_containment_escalation(self, router):
        query = IncidentQuery(
            raw_input="Status update", intent="status_update",
            entities={"containment_pct": 5.0},
        )
        result = await router.route(query)
        assert result.escalate is True

    @pytest.mark.asyncio
    async def test_red_flag_fire_escalation(self, router):
        query = IncidentQuery(raw_input="Red flag warning with active fire", intent="weather_check")
        result = await router.route(query)
        assert result.escalate is True

    @pytest.mark.asyncio
    async def test_no_escalation(self, router):
        query = IncidentQuery(raw_input="What is the weather?", intent="weather_check")
        result = await router.route(query)
        assert result.escalate is False
