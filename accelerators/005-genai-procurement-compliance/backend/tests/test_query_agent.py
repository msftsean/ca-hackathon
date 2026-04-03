"""QueryAgent unit tests."""

import pytest

from app.agents.query_agent import QueryAgent


@pytest.fixture
def agent():
    return QueryAgent()


@pytest.mark.asyncio
async def test_compliance_check_intent(agent):
    result = await agent.process("Check the compliance of this vendor")
    assert result.intent == "compliance_check"


@pytest.mark.asyncio
async def test_gap_analysis_intent(agent):
    result = await agent.process("What gaps are there in the attestation?")
    assert result.intent == "gap_analysis"


@pytest.mark.asyncio
async def test_attestation_upload_intent(agent):
    result = await agent.process("Upload a new attestation document")
    assert result.intent == "attestation_upload"


@pytest.mark.asyncio
async def test_risk_assessment_intent(agent):
    result = await agent.process("What is the risk classification?")
    assert result.intent == "risk_assessment"


@pytest.mark.asyncio
async def test_regulation_lookup_intent(agent):
    result = await agent.process("What are the EO requirements?")
    assert result.intent == "regulation_lookup"


@pytest.mark.asyncio
async def test_vendor_comparison_intent(agent):
    result = await agent.process("Compare vendors side by side")
    assert result.intent == "vendor_comparison"


@pytest.mark.asyncio
async def test_general_info_intent(agent):
    result = await agent.process("Tell me something")
    assert result.intent == "general_info"


@pytest.mark.asyncio
async def test_vendor_extraction(agent):
    result = await agent.process("Check compliance for AI Solutions Corp")
    assert result.entities.get("vendor_name") == "Ai Solutions Corp"


@pytest.mark.asyncio
async def test_document_id_passed(agent):
    result = await agent.process("Review this document", document_id="DOC-001")
    assert result.entities["document_id"] == "DOC-001"
