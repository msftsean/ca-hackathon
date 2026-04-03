"""Tests for MockWildfireService — mock data and operations."""

import pytest
from app.services.mock_service import MockWildfireService


@pytest.fixture
def service():
    return MockWildfireService()


class TestIncidents:
    def test_get_all_incidents(self, service):
        incidents = service.get_all_incidents()
        assert len(incidents) >= 3

    def test_get_known_incident(self, service):
        inc = service.get_incident("CA-BTU-004521")
        assert inc is not None
        assert inc.name == "Paradise Ridge Fire"
        assert inc.severity == "major"
        assert inc.county == "Butte"

    def test_get_unknown_incident(self, service):
        inc = service.get_incident("CA-XXX-999999")
        assert inc is None

    def test_incident_types(self, service):
        incidents = service.get_all_incidents()
        types = {i.incident_type for i in incidents}
        assert "wildfire" in types
        assert "structure_fire" in types
        assert "flood" in types

    def test_create_incident(self, service):
        inc = service.create_incident({
            "name": "Test Fire",
            "location": "Test Location",
            "county": "Test County",
        })
        assert inc.incident_id.startswith("CA-NEW-")
        assert inc.status == "active"


class TestResources:
    def test_all_available(self, service):
        resources = service.get_available_resources()
        assert len(resources) > 0
        assert all(r.status == "available" for r in resources)

    def test_filter_by_type(self, service):
        resources = service.get_available_resources(["helicopter"])
        assert len(resources) > 0
        assert all(r.resource_type == "helicopter" for r in resources)

    def test_resource_types_diverse(self, service):
        all_resources = service.RESOURCES
        types = {r.resource_type for r in all_resources}
        assert "engine" in types
        assert "crew" in types
        assert "helicopter" in types
        assert "dozer" in types

    def test_total_resources(self, service):
        assert len(service.RESOURCES) >= 15


class TestEvacuation:
    def test_evacuation_info(self, service):
        info = service.get_evacuation_info()
        assert len(info.zones) >= 4
        assert info.total_evacuated > 0
        assert info.shelters_open > 0

    def test_evacuation_zones_have_routes(self, service):
        info = service.get_evacuation_info()
        zones_with_routes = [z for z in info.zones if z.routes]
        assert len(zones_with_routes) > 0

    def test_evacuation_statuses(self, service):
        info = service.get_evacuation_info()
        statuses = {z.status for z in info.zones}
        assert "order" in statuses
        assert "warning" in statuses


class TestWeather:
    def test_all_weather(self, service):
        weather = service.get_weather()
        assert len(weather) >= 3

    def test_weather_by_county(self, service):
        weather = service.get_weather("Butte")
        assert len(weather) == 1
        assert weather[0].red_flag_warning is True

    def test_weather_unknown_county(self, service):
        weather = service.get_weather("Nonexistent")
        assert len(weather) == 0

    def test_red_flag_exists(self, service):
        weather = service.get_weather()
        has_red_flag = any(w.red_flag_warning for w in weather)
        assert has_red_flag


class TestPSPS:
    def test_psps_events(self, service):
        events = service.get_psps_events()
        assert len(events) >= 2

    def test_psps_utilities(self, service):
        events = service.get_psps_events()
        utilities = {e.utility for e in events}
        assert "PGE" in utilities
        assert "SCE" in utilities

    def test_psps_statuses(self, service):
        events = service.get_psps_events()
        statuses = {e.status for e in events}
        assert "active" in statuses
        assert "planned" in statuses


class TestAgencyAssignments:
    def test_assignments(self, service):
        assignments = service.get_agency_assignments()
        assert len(assignments) >= 5

    def test_agencies_present(self, service):
        assignments = service.get_agency_assignments()
        agencies = {a.agency for a in assignments}
        assert "CAL_FIRE" in agencies
        assert "Cal_OES" in agencies
