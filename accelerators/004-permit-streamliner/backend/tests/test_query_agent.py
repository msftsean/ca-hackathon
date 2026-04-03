"""Tests for the QueryAgent."""

import pytest
from app.agents.query_agent import QueryAgent


@pytest.fixture
def agent():
    return QueryAgent()


@pytest.mark.asyncio
async def test_detect_project_intake_intent(agent):
    query = await agent.process("I want to build an addition")
    assert query.intent == "project_intake"


@pytest.mark.asyncio
async def test_detect_requirement_check_intent(agent):
    query = await agent.process("What documents do I need for a permit?")
    assert query.intent == "requirement_check"


@pytest.mark.asyncio
async def test_detect_zoning_check_intent(agent):
    query = await agent.process("What is the zoning for this address?")
    assert query.intent == "zoning_check"


@pytest.mark.asyncio
async def test_detect_status_check_intent(agent):
    query = await agent.process("What is the status of my application?")
    assert query.intent == "status_check"


@pytest.mark.asyncio
async def test_detect_fee_estimate_intent(agent):
    query = await agent.process("How much does a permit cost?")
    assert query.intent == "fee_estimate"


@pytest.mark.asyncio
async def test_detect_general_info_intent(agent):
    query = await agent.process("I have a question about the permit process")
    assert query.intent == "general_info"


@pytest.mark.asyncio
async def test_extract_project_type_addition(agent):
    query = await agent.process("I want to build an addition")
    assert query.project_type == "addition"


@pytest.mark.asyncio
async def test_extract_project_type_adu(agent):
    query = await agent.process("I want to build an ADU")
    assert query.project_type == "adu"


@pytest.mark.asyncio
async def test_extract_project_type_commercial(agent):
    query = await agent.process("Commercial office renovation")
    assert query.project_type == "commercial"


@pytest.mark.asyncio
async def test_extract_project_type_demolition(agent):
    query = await agent.process("I need to demolish a building")
    assert query.project_type == "demolition"


@pytest.mark.asyncio
async def test_extract_square_footage(agent):
    query = await agent.process("I want to build a 500 sq ft addition")
    assert query.entities.get("square_footage") == 500


@pytest.mark.asyncio
async def test_extract_address(agent):
    query = await agent.process("What is the zoning for 123 Main St?")
    assert query.address is not None
    assert "123 Main St" in query.address


@pytest.mark.asyncio
async def test_no_project_type_for_general(agent):
    query = await agent.process("I have a question about permits")
    assert query.project_type is None
