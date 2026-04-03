"""QueryAgent unit tests."""

import pytest

from app.agents.query_agent import QueryAgent


@pytest.fixture
def agent():
    return QueryAgent()


@pytest.mark.asyncio
async def test_shelter_intent(agent):
    result = await agent.process("Where is the nearest shelter?")
    assert result.intent == "shelter_search"


@pytest.mark.asyncio
async def test_air_quality_intent(agent):
    result = await agent.process("What is the air quality in Sacramento?")
    assert result.intent == "air_quality"


@pytest.mark.asyncio
async def test_wildfire_alert_intent(agent):
    result = await agent.process("Are there any wildfire alerts?")
    assert result.intent == "active_alerts"
    assert result.emergency_type == "wildfire"


@pytest.mark.asyncio
async def test_evacuation_intent(agent):
    result = await agent.process("Is there an evacuation order?")
    assert result.intent == "evacuation_status"


@pytest.mark.asyncio
async def test_general_query(agent):
    result = await agent.process("Tell me something")
    assert result.intent == "general_info"


@pytest.mark.asyncio
async def test_safety_tips_intent(agent):
    result = await agent.process("How do I prepare an emergency kit?")
    assert result.intent == "safety_tips"


@pytest.mark.asyncio
async def test_pii_detection_ssn(agent):
    result = await agent.process("My SSN is 123-45-6789")
    assert result.entities["has_pii"] is True
    assert result.raw_input == "[PII REDACTED]"


@pytest.mark.asyncio
async def test_pii_not_detected(agent):
    result = await agent.process("Is there a fire?")
    assert result.entities["has_pii"] is False


@pytest.mark.asyncio
async def test_location_extraction_zip(agent):
    result = await agent.process("Alerts near 95814")
    assert result.location == "95814"


@pytest.mark.asyncio
async def test_earthquake_type(agent):
    result = await agent.process("Was there an earthquake?")
    assert result.emergency_type == "earthquake"


@pytest.mark.asyncio
async def test_flood_type(agent):
    result = await agent.process("Flood warning in my area")
    assert result.emergency_type == "flood"
