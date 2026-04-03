"""RouterAgent unit tests."""

import pytest

from app.agents.router_agent import RouterAgent
from app.models.schemas import EmergencyQuery


@pytest.fixture
def router():
    return RouterAgent()


def _make_query(intent: str, emergency_type: str | None = None) -> EmergencyQuery:
    return EmergencyQuery(
        raw_input="test",
        intent=intent,
        language="en",
        emergency_type=emergency_type,
    )


@pytest.mark.asyncio
async def test_evacuation_critical(router):
    result = await router.route(_make_query("evacuation_status", "wildfire"))
    assert result.priority == "critical"
    assert result.escalate is True


@pytest.mark.asyncio
async def test_active_alerts_critical(router):
    result = await router.route(_make_query("active_alerts", "earthquake"))
    assert result.priority == "critical"


@pytest.mark.asyncio
async def test_shelter_high(router):
    result = await router.route(_make_query("shelter_search"))
    assert result.priority == "high"


@pytest.mark.asyncio
async def test_air_quality_medium(router):
    result = await router.route(_make_query("air_quality"))
    assert result.priority == "medium"


@pytest.mark.asyncio
async def test_general_low(router):
    result = await router.route(_make_query("general_info"))
    assert result.priority == "low"


@pytest.mark.asyncio
async def test_safety_tips_low(router):
    result = await router.route(_make_query("safety_tips"))
    assert result.priority == "low"


@pytest.mark.asyncio
async def test_department_routing(router):
    result = await router.route(_make_query("shelter_search"))
    assert result.department == "cal_oes_shelters"


@pytest.mark.asyncio
async def test_no_escalation_general(router):
    result = await router.route(_make_query("general_info"))
    assert result.escalate is False
