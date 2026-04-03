"""QueryAgent unit tests."""

import pytest
from app.agents.query_agent import QueryAgent


@pytest.fixture
def agent():
    return QueryAgent()


@pytest.mark.asyncio
async def test_detect_policy_intent(agent):
    result = await agent.process("Find the policy on telework")
    assert result.intent == "policy_search"


@pytest.mark.asyncio
async def test_detect_expert_intent(agent):
    result = await agent.process("Who is the expert on procurement?")
    assert result.intent == "expert_search"


@pytest.mark.asyncio
async def test_detect_document_intent(agent):
    result = await agent.process("Find and retrieve document POL-001")
    assert result.intent == "document_lookup"


@pytest.mark.asyncio
async def test_detect_cross_reference_intent(agent):
    result = await agent.process("What related cross-reference supersedes this?")
    assert result.intent == "cross_reference"


@pytest.mark.asyncio
async def test_detect_agency_intent(agent):
    result = await agent.process("Tell me about the agency departments")
    assert result.intent == "agency_info"


@pytest.mark.asyncio
async def test_extract_agencies(agent):
    result = await agent.process("Search CDSS and EDD policies")
    assert "CDSS" in result.agencies
    assert "EDD" in result.agencies


@pytest.mark.asyncio
async def test_extract_document_types(agent):
    result = await agent.process("Find regulation and guidance documents")
    assert "regulation" in result.document_types
    assert "guidance" in result.document_types


@pytest.mark.asyncio
async def test_extract_keywords(agent):
    result = await agent.process("CalFresh eligibility requirements")
    assert len(result.keywords) > 0


@pytest.mark.asyncio
async def test_agency_filter_passthrough(agent):
    result = await agent.process(
        "Search policies",
        agency_filter=["DHCS"],
    )
    assert result.agencies == ["DHCS"]
