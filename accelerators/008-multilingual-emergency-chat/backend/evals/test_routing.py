"""Routing evaluation — verifies routing decisions per intent."""

import pytest

from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent

query_agent = QueryAgent()
router_agent = RouterAgent()


ROUTING_CASES = [
    ("Are there wildfire alerts?", "critical"),
    ("Is there an evacuation order?", "critical"),
    ("Where is the nearest shelter?", "high"),
    ("What is the air quality?", "medium"),
    ("How do I prepare?", "low"),
    ("hello", "low"),
]


@pytest.mark.anyio
@pytest.mark.parametrize("message,expected_priority", ROUTING_CASES)
async def test_routing_priority(message, expected_priority):
    query = await query_agent.process(message)
    routing = await router_agent.route(query)
    assert routing.priority == expected_priority, (
        f"Expected {expected_priority} for '{message}', got {routing.priority}"
    )


@pytest.mark.anyio
async def test_escalation_on_wildfire_evacuation():
    query = await query_agent.process("Should I evacuate from the wildfire?")
    routing = await router_agent.route(query)
    assert routing.escalate is True


@pytest.mark.anyio
async def test_no_escalation_general():
    query = await query_agent.process("What can you help with?")
    routing = await router_agent.route(query)
    assert routing.escalate is False
