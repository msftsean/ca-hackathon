"""Pydantic model validation tests."""

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    AirQualityReport,
    ChatRequest,
    ChatResponse,
    Citation,
    EmergencyAlert,
    EmergencyQuery,
    EvacuationOrder,
    RoutingDecision,
    ShelterInfo,
)


def test_chat_request_valid():
    req = ChatRequest(message="hello")
    assert req.message == "hello"
    assert req.language == "en"
    assert req.session_id is None


def test_chat_request_missing_message():
    with pytest.raises(ValidationError):
        ChatRequest()  # type: ignore[call-arg]


def test_chat_request_custom_language():
    req = ChatRequest(message="hola", language="es")
    assert req.language == "es"


def test_chat_response_defaults():
    resp = ChatResponse(response="test")
    assert resp.language == "en"
    assert resp.confidence == 0.0
    assert resp.citations == []
    assert resp.alerts is None
    assert resp.shelters is None


def test_emergency_alert_valid():
    alert = EmergencyAlert(
        alert_id="A1",
        title="Test",
        description="Desc",
        severity="severe",
        emergency_type="wildfire",
    )
    assert alert.severity == "severe"
    assert alert.source == "Cal OES"


def test_emergency_alert_invalid_severity():
    with pytest.raises(ValidationError):
        EmergencyAlert(
            alert_id="A1",
            title="Test",
            description="Desc",
            severity="unknown",
            emergency_type="wildfire",
        )


def test_shelter_info_defaults():
    shelter = ShelterInfo(
        shelter_id="S1",
        name="Test Shelter",
        address="123 Main",
        city="Sacramento",
        county="Sacramento",
        capacity=100,
    )
    assert shelter.current_occupancy == 0
    assert shelter.accepts_pets is False
    assert shelter.ada_accessible is True
    assert shelter.status == "open"


def test_air_quality_valid():
    aqi = AirQualityReport(
        location="Test",
        aqi=150,
        category="unhealthy",
    )
    assert aqi.pollutant == "PM2.5"


def test_air_quality_invalid_category():
    with pytest.raises(ValidationError):
        AirQualityReport(
            location="Test",
            aqi=150,
            category="terrible",
        )


def test_evacuation_order_valid():
    order = EvacuationOrder(
        order_id="E1",
        zone_name="Zone A",
        status="mandatory",
    )
    assert order.routes == []


def test_routing_decision_valid():
    rd = RoutingDecision(
        department="cal_oes",
        priority="high",
        reason="test",
    )
    assert rd.escalate is False


def test_routing_decision_invalid_priority():
    with pytest.raises(ValidationError):
        RoutingDecision(
            department="cal_oes",
            priority="urgent",
            reason="test",
        )


def test_citation_valid():
    c = Citation(source="Cal OES", text="Test citation")
    assert c.url is None


def test_emergency_query_defaults():
    q = EmergencyQuery(raw_input="test")
    assert q.intent == "general_info"
    assert q.language == "en"
    assert q.entities == {}
