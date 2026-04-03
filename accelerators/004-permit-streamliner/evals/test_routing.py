"""Routing evaluation tests for Permit Streamliner."""

import pytest
from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent

query_agent = QueryAgent()
router_agent = RouterAgent()


ROUTING_CASES = [
    ("I want to build an addition", ["building", "zoning"]),
    ("What documents do I need for a permit?", ["building"]),
    ("What is the zoning for this property?", ["zoning"]),
    ("What is the status of my application?", ["building"]),
    ("How much does a permit cost?", ["building"]),
]


@pytest.mark.parametrize("message,expected_depts", ROUTING_CASES)
@pytest.mark.asyncio
async def test_routes_to_correct_departments(message, expected_depts):
    query = await query_agent.process(message)
    decision = await router_agent.route(query)
    for dept in expected_depts:
        assert dept in decision.departments, (
            f"Expected '{dept}' in departments but got {decision.departments} "
            f"for message: {message}"
        )


PRIORITY_CASES = [
    ("I want to build a new house", "high"),
    ("What documents do I need?", "medium"),
    ("How much does it cost?", "low"),
    ("What is my application status?", "high"),
]


@pytest.mark.parametrize("message,expected_priority", PRIORITY_CASES)
@pytest.mark.asyncio
async def test_routes_correct_priority(message, expected_priority):
    query = await query_agent.process(message)
    decision = await router_agent.route(query)
    assert decision.priority == expected_priority, (
        f"Expected priority '{expected_priority}' but got '{decision.priority}' "
        f"for message: {message}"
    )
