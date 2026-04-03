"""Routing evaluation tests for BenefitsCal Navigator."""

import pytest
from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent

query_agent = QueryAgent()
router_agent = RouterAgent()


ROUTING_CASES = [
    ("Am I eligible for CalFresh?", "eligibility_services"),
    ("How do I apply for CalWORKs?", "enrollment_services"),
    ("What documents do I need?", "document_processing"),
    ("Where is the nearest office?", "county_offices"),
    ("Check my application status", "enrollment_services"),
    ("Tell me about benefits", "general_support"),
    ("I need help with benefits", "general_support"),
    ("How do I sign up for CalFresh?", "enrollment_services"),
]


@pytest.mark.parametrize("message,expected_dept", ROUTING_CASES)
@pytest.mark.asyncio
async def test_routes_to_correct_department(message, expected_dept):
    query = await query_agent.process(message)
    decision = await router_agent.route(query)
    assert decision.department == expected_dept, (
        f"Expected department '{expected_dept}' but got '{decision.department}' "
        f"for message: {message}"
    )


PRIORITY_CASES = [
    ("How do I apply for CalFresh?", "high"),
    ("Check my application status", "high"),
    ("Am I eligible for CalFresh?", "medium"),
    ("Tell me about CalFresh", "low"),
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
