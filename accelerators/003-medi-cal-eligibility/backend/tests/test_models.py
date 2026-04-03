"""Tests for Pydantic models and FPL calculation."""

import pytest
from datetime import datetime
from app.models.schemas import (
    ChatRequest, ChatResponse, Citation, MediCalQuery,
    ApplicationInfo, EligibilityScreening, DocumentInfo,
    IncomeVerification, RoutingDecision, AgentResponse,
    ApplicationStatus,
)
from app.services.mock_service import MockMediCalService


class TestChatRequest:
    def test_defaults(self):
        req = ChatRequest(message="hello")
        assert req.message == "hello"
        assert req.language == "en"
        assert req.session_id is None
        assert req.application_id is None

    def test_all_fields(self):
        req = ChatRequest(message="test", language="es", session_id="s1", application_id="MC-1")
        assert req.language == "es"
        assert req.session_id == "s1"


class TestChatResponse:
    def test_minimal(self):
        resp = ChatResponse(response="Hello", confidence=0.9)
        assert resp.response == "Hello"
        assert resp.citations == []
        assert resp.eligibility is None
        assert resp.application is None


class TestEligibilityScreening:
    def test_eligible(self):
        s = EligibilityScreening(
            program_type="MAGI_Adult", likely_eligible=True,
            confidence=0.92, income_limit=20782.8, fpl_percentage=100.0,
        )
        assert s.likely_eligible is True
        assert s.program_type == "MAGI_Adult"

    def test_factors_list(self):
        s = EligibilityScreening(
            program_type="MAGI_Child", likely_eligible=True,
            confidence=0.9, income_limit=40059.6, fpl_percentage=50.0,
            factors=["Below threshold"],
        )
        assert len(s.factors) == 1


class TestApplicationInfo:
    def test_creation(self):
        app = ApplicationInfo(
            app_id="MC-001", applicant_name="Test User",
            household_size=2, monthly_income=2000.0, county="LA",
        )
        assert app.status == "draft"
        assert app.program_type == "MAGI_Adult"


class TestMediCalQuery:
    def test_defaults(self):
        q = MediCalQuery(raw_input="test")
        assert q.intent == "general_info"
        assert q.entities == {}
        assert q.program_type is None


class TestDocumentInfo:
    def test_creation(self):
        d = DocumentInfo(doc_id="d1", doc_type="W2")
        assert d.upload_status == "pending"
        assert d.extracted_data is None


class TestIncomeVerification:
    def test_defaults(self):
        v = IncomeVerification(source="employment", amount=3000.0)
        assert v.frequency == "monthly"
        assert v.verified is False


class TestRoutingDecision:
    def test_defaults(self):
        r = RoutingDecision(destination="eligibility_screening")
        assert r.priority == "medium"
        assert r.escalate is False


class TestFPLCalculation:
    """Test FPL calculation logic in mock service."""

    def setup_method(self):
        self.service = MockMediCalService()

    def test_individual_fpl(self):
        assert self.service.calculate_fpl(1) == 15060

    def test_two_person_fpl(self):
        assert self.service.calculate_fpl(2) == 15060 + 5380

    def test_four_person_fpl(self):
        expected = 15060 + 5380 * 3
        assert self.service.calculate_fpl(4) == expected

    def test_zero_household_defaults_to_one(self):
        assert self.service.calculate_fpl(0) == 15060

    def test_fpl_increases_per_person(self):
        fpl_3 = self.service.calculate_fpl(3)
        fpl_4 = self.service.calculate_fpl(4)
        assert fpl_4 - fpl_3 == 5380
