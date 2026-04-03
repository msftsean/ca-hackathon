"""Tests for Pydantic models."""

from datetime import datetime
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    Citation,
    PermitQuery,
    PermitApplication,
    PermitRequirement,
    ChecklistItem,
    DocumentChecklist,
    ZoningResult,
    RoutingDecision,
    SLAStatus,
    AgentResponse,
)


def test_chat_request_defaults():
    req = ChatRequest(message="Hello")
    assert req.message == "Hello"
    assert req.language == "en"
    assert req.session_id is None


def test_chat_request_full():
    req = ChatRequest(message="Build permit", language="es", session_id="sess-1")
    assert req.language == "es"


def test_citation():
    c = Citation(source="CBC", text="Building code", policy_ref="CBC 107.2")
    assert c.source == "CBC"
    assert c.url is None


def test_permit_query():
    q = PermitQuery(raw_input="build addition", intent="project_intake")
    assert q.entities == {}
    assert q.project_type is None


def test_permit_application():
    app = PermitApplication(
        app_id="PRM-001",
        applicant_name="Test",
        project_type="addition",
        project_description="500 sqft addition",
        address="123 Main St",
    )
    assert app.status == "draft"
    assert app.submitted_at is None


def test_permit_requirement():
    r = PermitRequirement(
        req_id="REQ-1",
        name="Site Plan",
        description="To-scale site plan",
        category="building",
    )
    assert r.required is True


def test_checklist_item():
    item = ChecklistItem(name="Site plan")
    assert item.required is True
    assert item.submitted is False
    assert item.status == "pending"


def test_document_checklist():
    dc = DocumentChecklist(items=[ChecklistItem(name="Plan")])
    assert len(dc.items) == 1


def test_zoning_result():
    zr = ZoningResult(
        address="123 Main St",
        zone_code="R-1",
        zone_name="Residential",
        permitted_uses=["Single-family"],
    )
    assert zr.compliant is True
    assert zr.max_height_ft == 35.0


def test_routing_decision():
    rd = RoutingDecision(
        departments=["building", "zoning"],
        priority="high",
        reason="Project intake",
    )
    assert rd.sla_days == 30


def test_sla_status():
    sla = SLAStatus(
        application_id="PRM-001",
        department="building",
        assigned_date=datetime(2025, 1, 1),
        due_date=datetime(2025, 1, 31),
    )
    assert sla.status == "on_track"
    assert sla.days_remaining == 30


def test_agent_response():
    ar = AgentResponse(
        intent="project_intake",
        response_text="Here are your requirements",
        confidence=0.90,
    )
    assert ar.data is None


def test_chat_response():
    r = ChatResponse(
        response="Test response",
        confidence=0.85,
        citations=[Citation(source="CBC", text="test")],
    )
    assert r.data is None
