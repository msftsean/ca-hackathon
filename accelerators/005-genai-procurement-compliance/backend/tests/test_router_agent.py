"""RouterAgent unit tests."""

import pytest

from app.agents.router_agent import RouterAgent
from app.models.schemas import ComplianceQuery


@pytest.fixture
def router():
    return RouterAgent()


def _make_query(intent: str) -> ComplianceQuery:
    return ComplianceQuery(raw_input="test", intent=intent)


@pytest.mark.asyncio
async def test_compliance_check_high(router):
    result = await router.route(_make_query("compliance_check"))
    assert result.priority == "high"
    assert result.department == "compliance_review"


@pytest.mark.asyncio
async def test_gap_analysis_high(router):
    result = await router.route(_make_query("gap_analysis"))
    assert result.priority == "high"


@pytest.mark.asyncio
async def test_risk_assessment_critical(router):
    result = await router.route(_make_query("risk_assessment"))
    assert result.priority == "critical"
    assert result.escalate is True


@pytest.mark.asyncio
async def test_attestation_upload_medium(router):
    result = await router.route(_make_query("attestation_upload"))
    assert result.priority == "medium"


@pytest.mark.asyncio
async def test_regulation_lookup_low(router):
    result = await router.route(_make_query("regulation_lookup"))
    assert result.priority == "low"


@pytest.mark.asyncio
async def test_general_low(router):
    result = await router.route(_make_query("general_info"))
    assert result.priority == "low"
    assert result.escalate is False


@pytest.mark.asyncio
async def test_vendor_comparison_medium(router):
    result = await router.route(_make_query("vendor_comparison"))
    assert result.priority == "medium"
