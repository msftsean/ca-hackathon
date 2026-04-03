"""Tests for Pydantic models."""

from datetime import datetime
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    Citation,
    ProgramInfo,
    EligibilityResult,
    BenefitQuery,
    AgentResponse,
    RoutingDecision,
    EscalationTicket,
    LanguagePreference,
)


def test_chat_request_defaults():
    req = ChatRequest(message="Hello")
    assert req.message == "Hello"
    assert req.language == "en"
    assert req.session_id is None
    assert req.county is None


def test_chat_request_full():
    req = ChatRequest(
        message="Am I eligible?",
        language="es",
        session_id="sess-123",
        county="Los Angeles",
    )
    assert req.language == "es"
    assert req.session_id == "sess-123"
    assert req.county == "Los Angeles"


def test_citation():
    c = Citation(source="CDSS", text="Policy text", policy_ref="MPP 63-503")
    assert c.source == "CDSS"
    assert c.url is None


def test_program_info():
    p = ProgramInfo(
        program_id="calfresh",
        name="CalFresh",
        description="Food benefits",
        agency="CDSS",
        requirements=["Be a CA resident"],
        documents_needed=["Photo ID"],
    )
    assert p.program_id == "calfresh"
    assert len(p.requirements) == 1


def test_eligibility_result():
    e = EligibilityResult(
        program="CalFresh",
        likely_eligible=True,
        confidence=0.92,
        factors=["Low income"],
        next_steps=["Apply online"],
    )
    assert e.likely_eligible is True
    assert e.confidence == 0.92


def test_benefit_query_defaults():
    q = BenefitQuery(raw_input="test", intent="general_info")
    assert q.language == "en"
    assert q.entities == {}
    assert q.county is None
    assert q.program is None


def test_chat_response():
    r = ChatResponse(
        response="Here is your answer",
        confidence=0.85,
        citations=[Citation(source="CDSS", text="test")],
    )
    assert r.confidence == 0.85
    assert r.programs is None
    assert r.eligibility is None


def test_agent_response():
    ar = AgentResponse(
        intent="eligibility_check",
        response_text="You may be eligible",
        confidence=0.90,
        citations=[],
    )
    assert ar.data is None


def test_routing_decision():
    rd = RoutingDecision(
        department="eligibility_services",
        priority="high",
        reason="Application help",
        escalate=False,
    )
    assert rd.department == "eligibility_services"


def test_escalation_ticket():
    et = EscalationTicket(
        ticket_id="ESC-001",
        reason="PII detected",
        priority="critical",
        created_at=datetime(2025, 1, 1, 12, 0),
    )
    assert et.ticket_id == "ESC-001"


def test_language_preference():
    lp = LanguagePreference(code="es", name="Spanish", supported=True)
    assert lp.supported is True
