"""Tests for Pydantic models."""

import pytest
from datetime import datetime
from app.models.schemas import (
    ChatRequest, ChatResponse, Citation, IncidentQuery,
    Incident, IncidentSummary, ResourceAllocation,
    EvacuationZone, EvacuationInfo, WeatherCondition,
    PSPSEvent, AgencyAssignment, RoutingDecision, AgentResponse,
)


class TestChatRequest:
    def test_defaults(self):
        req = ChatRequest(message="hello")
        assert req.message == "hello"
        assert req.session_id is None
        assert req.incident_id is None

    def test_all_fields(self):
        req = ChatRequest(message="test", session_id="s1", incident_id="CA-001")
        assert req.session_id == "s1"
        assert req.incident_id == "CA-001"


class TestChatResponse:
    def test_minimal(self):
        resp = ChatResponse(response="Hello", confidence=0.9)
        assert resp.response == "Hello"
        assert resp.citations == []
        assert resp.incident is None
        assert resp.resources is None
        assert resp.evacuation is None


class TestIncident:
    def test_creation(self):
        inc = Incident(
            incident_id="CA-TEST-001", name="Test Fire",
            location="Test Location", county="Test County",
        )
        assert inc.incident_type == "wildfire"
        assert inc.severity == "moderate"
        assert inc.status == "active"
        assert inc.lead_agency == "CAL FIRE"

    def test_all_types(self):
        for t in ["wildfire", "structure_fire", "flood", "earthquake", "hazmat"]:
            inc = Incident(incident_id="T", name="T", incident_type=t)
            assert inc.incident_type == t


class TestResourceAllocation:
    def test_defaults(self):
        r = ResourceAllocation(resource_id="R1", resource_type="engine")
        assert r.quantity == 1
        assert r.status == "available"
        assert r.eta_minutes is None
        assert r.mutual_aid_region == 1


class TestEvacuationZone:
    def test_defaults(self):
        z = EvacuationZone(zone_id="Z1", zone_name="Test Zone")
        assert z.status == "warning"
        assert z.population == 0
        assert z.routes == []
        assert z.shelters == []


class TestEvacuationInfo:
    def test_defaults(self):
        info = EvacuationInfo()
        assert info.zones == []
        assert info.total_evacuated == 0
        assert info.shelters_open == 0


class TestWeatherCondition:
    def test_creation(self):
        w = WeatherCondition(
            location="Test", temperature_f=95.0, humidity_pct=15.0,
            wind_speed_mph=20.0, wind_direction="NE",
        )
        assert w.red_flag_warning is False
        assert w.fire_weather_watch is False


class TestPSPSEvent:
    def test_creation(self):
        p = PSPSEvent(event_id="P1", utility="PGE")
        assert p.status == "planned"
        assert p.affected_customers == 0
        assert p.affected_areas == []


class TestAgencyAssignment:
    def test_creation(self):
        a = AgencyAssignment(agency="CAL_FIRE")
        assert a.role == ""
        assert a.resources_committed == 0


class TestRoutingDecision:
    def test_defaults(self):
        r = RoutingDecision(destination="incident_command")
        assert r.priority == "medium"
        assert r.escalate is False
        assert r.escalation_reason is None


class TestIncidentSummary:
    def test_creation(self):
        s = IncidentSummary(
            incident_id="CA-001", name="Test",
            incident_type="wildfire", severity="major",
            location="Test", status="active", lead_agency="CAL FIRE",
        )
        assert s.containment_pct is None
