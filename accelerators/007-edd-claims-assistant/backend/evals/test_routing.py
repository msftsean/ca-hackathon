"""Routing evaluation tests for EDD Claims Assistant."""

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
        ("Check my claim status", "claims_services"),
        ("Am I eligible for unemployment?", "eligibility"),
        ("How do I file a new claim?", "filing_assistance"),
        ("What documents do I need?", "document_processing"),
        ("When is my next payment?", "payments"),
        ("I want to appeal my denial", "appeals"),
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
        "I am so frustrated about my denied claim",
        "This is desperate, I need help now",
        "I am angry and want to sue",
    ]
    for msg in escalation_messages:
        query = await query_agent.process(msg)
        routing = await router_agent.route(query)
        assert routing.escalate is True, f"Should escalate for: {msg}"
        assert routing.priority == "critical", f"Should be critical for: {msg}"


@pytest.mark.asyncio
async def test_pii_triggers_escalation(query_agent, router_agent):
    query = await query_agent.process("My SSN is 123-45-6789")
    routing = await router_agent.route(query)
    assert routing.escalate is True
