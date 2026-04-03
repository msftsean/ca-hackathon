"""Tests for ActionAgent — response generation and eligibility screening."""

import pytest
import os
from app.agents.action_agent import ActionAgent
from app.models.schemas import MediCalQuery, RoutingDecision


@pytest.fixture
def agent():
    os.environ["USE_MOCK_SERVICES"] = "true"
    return ActionAgent()


class TestEligibilityScreening:
    @pytest.mark.asyncio
    async def test_eligible_response(self, agent):
        query = MediCalQuery(
            raw_input="I make $1,000/month, am I eligible?",
            intent="eligibility_check",
            entities={"income_amounts": [1000.0], "household_size": 1},
        )
        routing = RoutingDecision(destination="eligibility_screening")
        result = await agent.execute(query, routing)
        assert result.confidence > 0
        assert result.eligibility is not None
        assert result.eligibility.likely_eligible is True

    @pytest.mark.asyncio
    async def test_ineligible_response(self, agent):
        query = MediCalQuery(
            raw_input="I make $5,000/month",
            intent="eligibility_check",
            entities={"income_amounts": [5000.0], "household_size": 1},
        )
        routing = RoutingDecision(destination="eligibility_screening")
        result = await agent.execute(query, routing)
        assert result.eligibility is not None
        assert result.eligibility.likely_eligible is False

    @pytest.mark.asyncio
    async def test_eligibility_with_citations(self, agent):
        query = MediCalQuery(
            raw_input="I make $1,500/month",
            intent="eligibility_check",
            entities={"income_amounts": [1500.0]},
        )
        routing = RoutingDecision(destination="eligibility_screening")
        result = await agent.execute(query, routing)
        assert len(result.citations) > 0

    @pytest.mark.asyncio
    async def test_no_income_program_info(self, agent):
        query = MediCalQuery(raw_input="Tell me about MAGI", intent="program_info")
        routing = RoutingDecision(destination="eligibility_screening")
        result = await agent.execute(query, routing)
        assert "MAGI" in result.response or "medi-cal" in result.response.lower()


class TestApplicationProcessing:
    @pytest.mark.asyncio
    async def test_known_application(self, agent):
        query = MediCalQuery(
            raw_input="Check application status",
            intent="application_status",
            entities={"application_id": "MC-2025-00001"},
        )
        routing = RoutingDecision(destination="application_processing")
        result = await agent.execute(query, routing)
        assert result.application is not None
        assert "MC-2025-00001" in result.response

    @pytest.mark.asyncio
    async def test_unknown_application(self, agent):
        query = MediCalQuery(
            raw_input="Check application",
            intent="application_status",
            entities={},
        )
        routing = RoutingDecision(destination="application_processing")
        result = await agent.execute(query, routing)
        assert result.application is None
        assert "application ID" in result.response


class TestOtherRoutes:
    @pytest.mark.asyncio
    async def test_document_help(self, agent):
        query = MediCalQuery(raw_input="What documents do I need?", intent="document_help")
        routing = RoutingDecision(destination="document_verification")
        result = await agent.execute(query, routing)
        assert "documents" in result.response.lower() or "document" in result.response.lower()

    @pytest.mark.asyncio
    async def test_county_info_known(self, agent):
        query = MediCalQuery(
            raw_input="Office in Sacramento",
            intent="county_info",
            entities={"county": "Sacramento"},
        )
        routing = RoutingDecision(destination="county_services")
        result = await agent.execute(query, routing)
        assert "Sacramento" in result.response

    @pytest.mark.asyncio
    async def test_county_info_unknown(self, agent):
        query = MediCalQuery(raw_input="Where is the office?", intent="county_info", entities={})
        routing = RoutingDecision(destination="county_services")
        result = await agent.execute(query, routing)
        assert "county" in result.response.lower()

    @pytest.mark.asyncio
    async def test_income_review(self, agent):
        query = MediCalQuery(
            raw_input="I make $2,000/month",
            intent="income_verification",
            entities={"income_amounts": [2000.0]},
        )
        routing = RoutingDecision(destination="income_review")
        result = await agent.execute(query, routing)
        assert result.eligibility is not None
