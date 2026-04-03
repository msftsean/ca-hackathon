"""Tests for MockMediCalService — FPL calculations and mock data."""

import pytest
from app.services.mock_service import MockMediCalService


@pytest.fixture
def service():
    return MockMediCalService()


class TestFPLCalculation:
    def test_individual(self, service):
        assert service.calculate_fpl(1) == 15060

    def test_household_of_2(self, service):
        assert service.calculate_fpl(2) == 20440

    def test_household_of_4(self, service):
        assert service.calculate_fpl(4) == 31200

    def test_zero_defaults_to_one(self, service):
        assert service.calculate_fpl(0) == 15060

    def test_large_household(self, service):
        fpl = service.calculate_fpl(8)
        expected = 15060 + 5380 * 7
        assert fpl == expected


class TestEligibilityScreening:
    def test_eligible_low_income(self, service):
        result = service.screen_eligibility(monthly_income=1000.0, household_size=1)
        assert result.likely_eligible is True
        assert result.program_type == "MAGI_Adult"

    def test_ineligible_high_income(self, service):
        result = service.screen_eligibility(monthly_income=5000.0, household_size=1)
        assert result.likely_eligible is False

    def test_child_program_higher_limit(self, service):
        result = service.screen_eligibility(
            monthly_income=2500.0, household_size=1, program_type="MAGI_Child"
        )
        assert result.likely_eligible is True

    def test_pregnancy_program(self, service):
        result = service.screen_eligibility(
            monthly_income=2000.0, household_size=1, program_type="Pregnancy"
        )
        assert result.likely_eligible is True
        assert result.program_type == "Pregnancy"

    def test_screening_has_documents(self, service):
        result = service.screen_eligibility(monthly_income=1000.0)
        assert len(result.required_documents) > 0

    def test_screening_has_next_steps(self, service):
        result = service.screen_eligibility(monthly_income=1000.0)
        assert len(result.next_steps) > 0

    def test_fpl_percentage(self, service):
        result = service.screen_eligibility(monthly_income=1255.0, household_size=1)
        expected_pct = (1255.0 * 12 / 15060) * 100
        assert abs(result.fpl_percentage - round(expected_pct, 1)) < 0.2


class TestApplicationStatus:
    def test_known_application(self, service):
        status = service.get_application_status("MC-2025-00001")
        assert status is not None
        assert status.app_id == "MC-2025-00001"
        assert status.status == "pending_verification"

    def test_unknown_application(self, service):
        status = service.get_application_status("MC-9999-99999")
        assert status is None

    def test_none_application(self, service):
        status = service.get_application_status(None)
        assert status is None

    def test_approved_application(self, service):
        status = service.get_application_status("MC-2025-00002")
        assert status is not None
        assert status.status == "approved"


class TestCountyOffices:
    def test_known_county(self, service):
        office = service.get_county_office("Los Angeles")
        assert office is not None
        assert "phone" in office

    def test_unknown_county(self, service):
        office = service.get_county_office("Nonexistent")
        assert office is None

    def test_none_county(self, service):
        office = service.get_county_office(None)
        assert office is None


class TestProgramInfo:
    def test_magi_adult(self, service):
        info = service.get_program_info("MAGI_Adult")
        assert "138%" in info

    def test_pregnancy(self, service):
        info = service.get_program_info("Pregnancy")
        assert "213%" in info or "pregnant" in info.lower()

    def test_unknown_program(self, service):
        info = service.get_program_info("Unknown")
        assert len(info) > 0


class TestDocuments:
    def test_required_documents(self, service):
        docs = service.get_required_documents()
        assert len(docs) >= 4

    def test_documents_include_id(self, service):
        docs = service.get_required_documents()
        assert any("ID" in d or "id" in d.lower() for d in docs)


class TestCreateApplication:
    def test_create(self, service):
        app = service.create_application({
            "applicant_name": "Test User",
            "household_size": 2,
            "monthly_income": 1500.0,
            "county": "Sacramento",
        })
        assert app.app_id.startswith("MC-2025-")
        assert app.status == "draft"
        assert app.applicant_name == "Test User"

    def test_get_all(self, service):
        apps = service.get_all_applications()
        assert len(apps) >= 5
