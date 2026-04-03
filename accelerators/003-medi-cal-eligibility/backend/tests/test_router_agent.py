"""Tests for RouterAgent — routing and escalation logic."""

import pytest
from app.agents.router_agent import RouterAgent
from app.models.schemas import MediCalQuery


@pytest.fixture
def router():
    return RouterAgent()


class TestRouting:
    @pytest.mark.asyncio
    async def test_eligibility_route(self, router):
        query = MediCalQuery(raw_input="Am I eligible?", intent="eligibility_check")
        result = await router.route(query)
        assert result.destination == "eligibility_screening"

    @pytest.mark.asyncio
    async def test_application_route(self, router):
        query = MediCalQuery(raw_input="Check my application", intent="application_status")
        result = await router.route(query)
        assert result.destination == "application_processing"

    @pytest.mark.asyncio
    async def test_income_route(self, router):
        query = MediCalQuery(raw_input="Verify my income", intent="income_verification")
        result = await router.route(query)
        assert result.destination == "income_review"

    @pytest.mark.asyncio
    async def test_document_route(self, router):
        query = MediCalQuery(raw_input="Upload documents", intent="document_help")
        result = await router.route(query)
        assert result.destination == "document_verification"

    @pytest.mark.asyncio
    async def test_county_route(self, router):
        query = MediCalQuery(raw_input="Find county office", intent="county_info")
        result = await router.route(query)
        assert result.destination == "county_services"

    @pytest.mark.asyncio
    async def test_default_route(self, router):
        query = MediCalQuery(raw_input="Hello", intent="unknown_intent")
        result = await router.route(query)
        assert result.destination == "eligibility_screening"


class TestPriority:
    @pytest.mark.asyncio
    async def test_application_high_priority(self, router):
        query = MediCalQuery(raw_input="My application status", intent="application_status")
        result = await router.route(query)
        assert result.priority == "high"

    @pytest.mark.asyncio
    async def test_income_high_priority(self, router):
        query = MediCalQuery(raw_input="My income", intent="income_verification")
        result = await router.route(query)
        assert result.priority == "high"

    @pytest.mark.asyncio
    async def test_general_low_priority(self, router):
        query = MediCalQuery(raw_input="What programs exist?", intent="program_info")
        result = await router.route(query)
        assert result.priority == "low"


class TestEscalation:
    @pytest.mark.asyncio
    async def test_pregnancy_escalation(self, router):
        query = MediCalQuery(raw_input="I'm pregnant and need help", intent="eligibility_check")
        result = await router.route(query)
        assert result.escalate is True
        assert result.priority == "critical"

    @pytest.mark.asyncio
    async def test_disability_escalation(self, router):
        query = MediCalQuery(raw_input="I have a disability", intent="eligibility_check")
        result = await router.route(query)
        assert result.escalate is True

    @pytest.mark.asyncio
    async def test_emergency_escalation(self, router):
        query = MediCalQuery(raw_input="I need emergency medical help", intent="general_info")
        result = await router.route(query)
        assert result.escalate is True

    @pytest.mark.asyncio
    async def test_no_escalation(self, router):
        query = MediCalQuery(raw_input="What documents do I need?", intent="document_help")
        result = await router.route(query)
        assert result.escalate is False
