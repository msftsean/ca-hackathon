"""Tests for the RouterAgent."""

import pytest
from app.agents.router_agent import RouterAgent
from app.models.schemas import PermitQuery


@pytest.fixture
def agent():
    return RouterAgent()


def _make_query(intent: str, raw_input: str = "", project_type: str | None = None) -> PermitQuery:
    return PermitQuery(
        raw_input=raw_input or f"test query for {intent}",
        intent=intent,
        project_type=project_type,
    )


@pytest.mark.asyncio
async def test_route_project_intake(agent):
    query = _make_query("project_intake")
    decision = await agent.route(query)
    assert "building" in decision.departments
    assert decision.priority == "high"


@pytest.mark.asyncio
async def test_route_requirement_check(agent):
    query = _make_query("requirement_check")
    decision = await agent.route(query)
    assert "building" in decision.departments
    assert decision.priority == "medium"


@pytest.mark.asyncio
async def test_route_zoning_check(agent):
    query = _make_query("zoning_check")
    decision = await agent.route(query)
    assert "zoning" in decision.departments


@pytest.mark.asyncio
async def test_route_status_check(agent):
    query = _make_query("status_check")
    decision = await agent.route(query)
    assert decision.priority == "high"


@pytest.mark.asyncio
async def test_route_fee_estimate(agent):
    query = _make_query("fee_estimate")
    decision = await agent.route(query)
    assert decision.priority == "low"


@pytest.mark.asyncio
async def test_route_commercial_project(agent):
    query = _make_query("project_intake", project_type="commercial")
    decision = await agent.route(query)
    assert "building" in decision.departments
    assert "fire" in decision.departments
    assert "health" in decision.departments


@pytest.mark.asyncio
async def test_route_new_construction(agent):
    query = _make_query("project_intake", project_type="new_construction")
    decision = await agent.route(query)
    assert "environmental_review" in decision.departments
    assert decision.sla_days >= 30


@pytest.mark.asyncio
async def test_route_demolition(agent):
    query = _make_query("project_intake", project_type="demolition")
    decision = await agent.route(query)
    assert "environmental_review" in decision.departments


@pytest.mark.asyncio
async def test_no_escalate_normal(agent):
    query = _make_query("project_intake", raw_input="I want to build an addition")
    decision = await agent.route(query)
    assert decision.escalate is False


@pytest.mark.asyncio
async def test_sla_days_set(agent):
    query = _make_query("project_intake", project_type="new_construction")
    decision = await agent.route(query)
    assert decision.sla_days > 0
