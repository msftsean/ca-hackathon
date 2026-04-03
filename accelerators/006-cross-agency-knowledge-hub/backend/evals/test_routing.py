"""Routing evaluation tests for Cross-Agency Knowledge Hub."""

import pytest
from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent


@pytest.fixture
def query_agent():
    return QueryAgent()


@pytest.fixture
def router_agent():
    return RouterAgent()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message,expected_dept",
    [
        ("Find policy on telework", "search_index"),
        ("Who is the procurement expert?", "expert_directory"),
        ("What cross-references exist for this?", "cross_reference_engine"),
        ("Tell me about the agency departments", "agency_directory"),
        ("Search for CalFresh regulations", "search_index"),
    ],
)
async def test_routing_department(query_agent, router_agent, message, expected_dept):
    query = await query_agent.process(message)
    routing = await router_agent.route(query)
    assert routing.department == expected_dept, (
        f"Expected {expected_dept}, got {routing.department} for: {message}"
    )


@pytest.mark.asyncio
async def test_escalation_triggers(query_agent, router_agent):
    escalation_messages = [
        "I need access to confidential documents",
        "This is urgent and restricted information",
        "Critical security issue with the system",
    ]
    for msg in escalation_messages:
        query = await query_agent.process(msg)
        routing = await router_agent.route(query)
        assert routing.escalate is True, f"Should escalate for: {msg}"
        assert routing.priority == "critical", f"Should be critical for: {msg}"
