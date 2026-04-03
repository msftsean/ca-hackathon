"""Schema model tests."""

from datetime import datetime
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    Citation,
    CrossReference,
    DocumentResult,
    ExpertInfo,
    SearchQuery,
    AgencyPermission,
    AgentResponse,
    RoutingDecision,
)


def test_chat_request_defaults():
    req = ChatRequest(message="test")
    assert req.language == "en"
    assert req.session_id is None
    assert req.agency_filter is None
    assert req.document_types is None


def test_chat_request_full():
    req = ChatRequest(
        message="test",
        language="es",
        session_id="sess-123",
        agency_filter=["CDSS", "EDD"],
        document_types=["policy"],
    )
    assert req.agency_filter == ["CDSS", "EDD"]
    assert req.document_types == ["policy"]


def test_chat_response():
    resp = ChatResponse(
        response="Test response",
        confidence=0.9,
        citations=[Citation(source="Test", text="citation")],
    )
    assert resp.confidence == 0.9
    assert resp.documents is None
    assert resp.experts is None
    assert resp.cross_references is None


def test_citation():
    c = Citation(source="Policy Manual", text="Section 1", agency="CDSS", document_id="DOC-001")
    assert c.agency == "CDSS"
    assert c.document_id == "DOC-001"


def test_document_result():
    doc = DocumentResult(
        doc_id="DOC-001",
        title="Test Policy",
        agency="CDSS",
        department="Test Div",
        document_type="policy",
        summary="Test summary",
        relevance_score=0.9,
        last_updated=datetime(2024, 1, 1),
        access_level="public",
    )
    assert doc.doc_id == "DOC-001"
    assert doc.access_level == "public"


def test_cross_reference():
    ref = CrossReference(
        source_doc_id="DOC-001",
        target_doc_id="DOC-002",
        relationship="supersedes",
        description="Test",
    )
    assert ref.relationship == "supersedes"


def test_expert_info():
    exp = ExpertInfo(
        expert_id="EXP-001",
        name="Test Expert",
        agency="CDSS",
        department="Test Div",
        expertise_areas=["policy"],
        email="test@ca.gov",
        available=True,
    )
    assert exp.available is True


def test_search_query():
    q = SearchQuery(
        raw_input="test",
        intent="policy_search",
        agencies=["CDSS"],
        keywords=["policy"],
    )
    assert q.intent == "policy_search"


def test_agency_permission():
    p = AgencyPermission(
        agency_code="CDSS",
        agency_name="CA Dept of Social Services",
        access_level="full",
        departments=["Div A"],
    )
    assert p.agency_code == "CDSS"


def test_agent_response():
    r = AgentResponse(
        intent="policy_search",
        response_text="Found policies",
        confidence=0.9,
    )
    assert r.data is None


def test_routing_decision():
    d = RoutingDecision(
        department="search_index",
        priority="high",
        reason="Test",
        escalate=False,
    )
    assert d.escalate is False
