"""Tests for the RouterAgent."""

import pytest
from app.agents.router_agent import RouterAgent
from app.models.schemas import BenefitQuery


@pytest.fixture
def agent():
    return RouterAgent()


def _make_query(intent: str, raw_input: str = "", **kwargs) -> BenefitQuery:
    return BenefitQuery(
        raw_input=raw_input or f"test query for {intent}",
        intent=intent,
        entities=kwargs.get("entities", {}),
    )


@pytest.mark.asyncio
async def test_route_eligibility_check(agent):
    query = _make_query("eligibility_check")
    decision = await agent.route(query)
    assert decision.department == "eligibility_services"
    assert decision.priority == "medium"


@pytest.mark.asyncio
async def test_route_application_help(agent):
    query = _make_query("application_help")
    decision = await agent.route(query)
    assert decision.department == "enrollment_services"
    assert decision.priority == "high"


@pytest.mark.asyncio
async def test_route_document_requirements(agent):
    query = _make_query("document_requirements")
    decision = await agent.route(query)
    assert decision.department == "document_processing"


@pytest.mark.asyncio
async def test_route_office_locations(agent):
    query = _make_query("office_locations")
    decision = await agent.route(query)
    assert decision.department == "county_offices"


@pytest.mark.asyncio
async def test_route_status_check(agent):
    query = _make_query("status_check")
    decision = await agent.route(query)
    assert decision.department == "enrollment_services"
    assert decision.priority == "high"


@pytest.mark.asyncio
async def test_route_general_info(agent):
    query = _make_query("general_info")
    decision = await agent.route(query)
    assert decision.department == "general_support"
    assert decision.priority == "low"


@pytest.mark.asyncio
async def test_escalate_on_pii(agent):
    query = _make_query(
        "eligibility_check",
        raw_input="My SSN is 123-45-6789",
        entities={"pii_detected": True},
    )
    decision = await agent.route(query)
    assert decision.escalate is True
    assert decision.priority == "critical"


@pytest.mark.asyncio
async def test_escalate_on_complaint(agent):
    query = _make_query(
        "general_info",
        raw_input="I want to file a complaint about my case",
    )
    decision = await agent.route(query)
    assert decision.escalate is True
    assert decision.priority == "critical"


@pytest.mark.asyncio
async def test_escalate_on_appeal(agent):
    query = _make_query(
        "general_info",
        raw_input="I need to appeal my denial",
    )
    decision = await agent.route(query)
    assert decision.escalate is True


@pytest.mark.asyncio
async def test_no_escalate_normal_query(agent):
    query = _make_query("eligibility_check", raw_input="Am I eligible for CalFresh?")
    decision = await agent.route(query)
    assert decision.escalate is False
