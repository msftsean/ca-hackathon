"""RouterAgent unit tests."""

import pytest
from app.agents.router_agent import RouterAgent
from app.models.schemas import SearchQuery


@pytest.fixture
def agent():
    return RouterAgent()


@pytest.mark.asyncio
async def test_route_policy_search(agent):
    query = SearchQuery(
        raw_input="Find policy on telework",
        intent="policy_search",
        agencies=["CalHR"],
        keywords=["telework"],
    )
    result = await agent.route(query)
    assert result.department == "search_index"
    assert result.priority == "high"


@pytest.mark.asyncio
async def test_route_expert_search(agent):
    query = SearchQuery(
        raw_input="Who is the procurement expert?",
        intent="expert_search",
        agencies=[],
        keywords=["procurement"],
    )
    result = await agent.route(query)
    assert result.department == "expert_directory"


@pytest.mark.asyncio
async def test_route_cross_reference(agent):
    query = SearchQuery(
        raw_input="Related documents",
        intent="cross_reference",
        agencies=[],
        keywords=["related"],
    )
    result = await agent.route(query)
    assert result.department == "cross_reference_engine"


@pytest.mark.asyncio
async def test_route_agency_info(agent):
    query = SearchQuery(
        raw_input="Tell me about the agency",
        intent="agency_info",
        agencies=[],
        keywords=["agency"],
    )
    result = await agent.route(query)
    assert result.department == "agency_directory"


@pytest.mark.asyncio
async def test_escalation_on_confidential(agent):
    query = SearchQuery(
        raw_input="I need access to confidential documents",
        intent="document_lookup",
        agencies=[],
        keywords=["confidential"],
    )
    result = await agent.route(query)
    assert result.escalate is True
    assert result.priority == "critical"


@pytest.mark.asyncio
async def test_no_escalation_normal(agent):
    query = SearchQuery(
        raw_input="Search for public policies",
        intent="policy_search",
        agencies=[],
        keywords=["public"],
    )
    result = await agent.route(query)
    assert result.escalate is False
