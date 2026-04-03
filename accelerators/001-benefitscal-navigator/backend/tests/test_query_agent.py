"""Tests for the QueryAgent."""

import pytest
from app.agents.query_agent import QueryAgent


@pytest.fixture
def agent():
    return QueryAgent()


@pytest.mark.asyncio
async def test_detect_eligibility_intent(agent):
    query = await agent.process("Am I eligible for CalFresh?")
    assert query.intent == "eligibility_check"


@pytest.mark.asyncio
async def test_detect_program_info_intent(agent):
    query = await agent.process("What is CalWORKs?")
    assert query.intent == "program_info"


@pytest.mark.asyncio
async def test_detect_application_help_intent(agent):
    query = await agent.process("How do I apply for benefits?")
    assert query.intent == "application_help"


@pytest.mark.asyncio
async def test_detect_document_intent(agent):
    query = await agent.process("What documents do I need?")
    assert query.intent == "document_requirements"


@pytest.mark.asyncio
async def test_detect_office_intent(agent):
    query = await agent.process("Where is the nearest office?")
    assert query.intent == "office_locations"


@pytest.mark.asyncio
async def test_detect_status_intent(agent):
    query = await agent.process("Check my application status")
    assert query.intent == "status_check"


@pytest.mark.asyncio
async def test_extract_program_calfresh(agent):
    query = await agent.process("Tell me about CalFresh")
    assert query.program == "calfresh"


@pytest.mark.asyncio
async def test_extract_program_calworks(agent):
    query = await agent.process("Am I eligible for CalWORKs?")
    assert query.program == "calworks"


@pytest.mark.asyncio
async def test_extract_program_general_relief(agent):
    query = await agent.process("How do I apply for general relief?")
    assert query.program == "general_relief"


@pytest.mark.asyncio
async def test_extract_county(agent):
    query = await agent.process("Where is the office in San Francisco?")
    assert query.county == "San Francisco"
    assert query.entities.get("county") == "San Francisco"


@pytest.mark.asyncio
async def test_detect_pii_ssn(agent):
    query = await agent.process("My SSN is 123-45-6789")
    assert query.entities.get("pii_detected") is True


@pytest.mark.asyncio
async def test_detect_pii_dob(agent):
    query = await agent.process("My date of birth is 01/15/1990")
    assert query.entities.get("pii_detected") is True


@pytest.mark.asyncio
async def test_no_pii_in_normal_query(agent):
    query = await agent.process("Am I eligible for CalFresh?")
    assert query.entities.get("pii_detected") is None


@pytest.mark.asyncio
async def test_extract_income(agent):
    query = await agent.process("I make $2,500 per month")
    assert "income_mentioned" in query.entities


@pytest.mark.asyncio
async def test_language_passthrough(agent):
    query = await agent.process("Ayuda con beneficios", language="es")
    assert query.language == "es"


@pytest.mark.asyncio
async def test_county_override(agent):
    query = await agent.process("Office locations", county="Sacramento")
    assert query.county == "Sacramento"
