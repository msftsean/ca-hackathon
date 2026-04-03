"""QueryAgent unit tests."""

import pytest
from app.agents.query_agent import QueryAgent


@pytest.fixture
def agent():
    return QueryAgent()


@pytest.mark.asyncio
async def test_detect_claim_status_intent(agent):
    result = await agent.process("Check my claim status")
    assert result.intent == "claim_status"


@pytest.mark.asyncio
async def test_detect_eligibility_intent(agent):
    result = await agent.process("Am I eligible for unemployment?")
    assert result.intent == "eligibility_check"


@pytest.mark.asyncio
async def test_detect_filing_intent(agent):
    result = await agent.process("How do I file a new claim?")
    assert result.intent == "filing_help"


@pytest.mark.asyncio
async def test_detect_document_intent(agent):
    result = await agent.process("What documents do I need to upload?")
    assert result.intent == "document_requirements"


@pytest.mark.asyncio
async def test_detect_payment_intent(agent):
    result = await agent.process("When will I get my payment deposit?")
    assert result.intent == "payment_info"


@pytest.mark.asyncio
async def test_detect_appeal_intent(agent):
    result = await agent.process("My claim was denied and I want to appeal")
    assert result.intent == "appeal_info"


@pytest.mark.asyncio
async def test_extract_claim_type_ui(agent):
    result = await agent.process("I was laid off and need unemployment")
    assert result.claim_type == "UI"


@pytest.mark.asyncio
async def test_extract_claim_type_di(agent):
    result = await agent.process("I need disability insurance")
    assert result.claim_type == "DI"


@pytest.mark.asyncio
async def test_extract_claim_type_pfl(agent):
    result = await agent.process("I need paid family leave for bonding")
    assert result.claim_type == "PFL"


@pytest.mark.asyncio
async def test_pii_detection(agent):
    result = await agent.process("My SSN is 123-45-6789")
    assert result.entities.get("pii_detected") is True
