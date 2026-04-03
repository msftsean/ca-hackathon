"""RouterAgent unit tests."""

import pytest
from app.agents.router_agent import RouterAgent
from app.models.schemas import ClaimQuery


@pytest.fixture
def agent():
    return RouterAgent()


@pytest.mark.asyncio
async def test_route_claim_status(agent):
    query = ClaimQuery(
        raw_input="Check my claim status",
        intent="claim_status",
    )
    result = await agent.route(query)
    assert result.department == "claims_services"
    assert result.priority == "medium"


@pytest.mark.asyncio
async def test_route_eligibility(agent):
    query = ClaimQuery(
        raw_input="Am I eligible?",
        intent="eligibility_check",
    )
    result = await agent.route(query)
    assert result.department == "eligibility"


@pytest.mark.asyncio
async def test_route_filing(agent):
    query = ClaimQuery(
        raw_input="File a new claim",
        intent="filing_help",
    )
    result = await agent.route(query)
    assert result.department == "filing_assistance"
    assert result.priority == "high"


@pytest.mark.asyncio
async def test_route_appeal(agent):
    query = ClaimQuery(
        raw_input="I want to appeal",
        intent="appeal_info",
    )
    result = await agent.route(query)
    assert result.department == "appeals"
    assert result.escalate is True
    assert result.priority == "critical"


@pytest.mark.asyncio
async def test_escalation_on_emotional_distress(agent):
    query = ClaimQuery(
        raw_input="I am so frustrated and angry about my claim",
        intent="general_info",
    )
    result = await agent.route(query)
    assert result.escalate is True
    assert result.priority == "critical"


@pytest.mark.asyncio
async def test_escalation_on_pii(agent):
    query = ClaimQuery(
        raw_input="Check claim",
        intent="claim_status",
        entities={"pii_detected": True},
    )
    result = await agent.route(query)
    assert result.escalate is True


@pytest.mark.asyncio
async def test_no_escalation_normal(agent):
    query = ClaimQuery(
        raw_input="How do I certify for benefits?",
        intent="general_info",
    )
    result = await agent.route(query)
    assert result.escalate is False
