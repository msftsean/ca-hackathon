"""Schema model tests."""

from datetime import datetime
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    Citation,
    ClaimQuery,
    ClaimStatus,
    DocumentItem,
    EligibilityAssessment,
    IdentityVerification,
    PolicyArticle,
    SupportTicket,
    AgentResponse,
    RoutingDecision,
)


def test_chat_request_defaults():
    req = ChatRequest(message="test")
    assert req.language == "en"
    assert req.session_id is None


def test_chat_response():
    resp = ChatResponse(
        response="Test response",
        confidence=0.9,
        citations=[Citation(source="EDD", text="test")],
    )
    assert resp.confidence == 0.9
    assert resp.claim_status is None
    assert resp.eligibility is None
    assert resp.document_checklist is None


def test_citation():
    c = Citation(source="EDD Policy", text="Section 1", policy_ref="CUIC §1253")
    assert c.policy_ref == "CUIC §1253"


def test_claim_query():
    q = ClaimQuery(
        raw_input="test",
        intent="claim_status",
        claim_type="UI",
    )
    assert q.claim_type == "UI"
    assert q.entities == {}


def test_claim_status():
    cs = ClaimStatus(
        claim_id="UI-001",
        claim_type="UI",
        status="active",
        filed_date=datetime(2025, 1, 1),
        weekly_benefit_amount=450.0,
        remaining_balance=9000.0,
    )
    assert cs.status == "active"
    assert cs.pending_issues == []


def test_eligibility_assessment():
    ea = EligibilityAssessment(
        claim_type="UI",
        likely_eligible=True,
        confidence=0.85,
        factors=["Factor 1"],
        requirements=["Req 1"],
        next_steps=["Step 1"],
    )
    assert ea.likely_eligible is True


def test_document_item():
    di = DocumentItem(
        name="Photo ID",
        required=True,
        submitted=False,
        description="Government-issued ID",
    )
    assert di.required is True
    assert di.submitted is False


def test_identity_verification():
    iv = IdentityVerification(
        last_four_ssn="1234",
        date_of_birth="01/15/1990",
        verified=True,
    )
    assert iv.verified is True


def test_policy_article():
    pa = PolicyArticle(
        article_id="POL-001",
        title="Test Policy",
        content="Content",
        claim_types=["UI", "DI"],
        last_updated=datetime(2024, 1, 1),
    )
    assert "UI" in pa.claim_types


def test_support_ticket():
    st = SupportTicket(
        ticket_id="TKT-001",
        reason="Claim denied",
        priority="high",
        claim_type="UI",
    )
    assert st.priority == "high"


def test_agent_response():
    r = AgentResponse(
        intent="claim_status",
        response_text="Your claim is active",
        confidence=0.9,
    )
    assert r.data is None


def test_routing_decision():
    d = RoutingDecision(
        department="claims_services",
        priority="medium",
        reason="Test",
        escalate=False,
    )
    assert d.escalate is False
