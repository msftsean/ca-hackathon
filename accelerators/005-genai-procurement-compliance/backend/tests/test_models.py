"""Pydantic model validation tests."""

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    AttestationDocument,
    ChatRequest,
    ChatResponse,
    Citation,
    ComplianceGap,
    ComplianceQuery,
    ComplianceResult,
    ComplianceRule,
    ComplianceScore,
    GapAnalysis,
    RiskClassification,
    RoutingDecision,
)


def test_chat_request_valid():
    req = ChatRequest(message="hello")
    assert req.message == "hello"
    assert req.session_id is None
    assert req.document_id is None


def test_chat_request_missing_message():
    with pytest.raises(ValidationError):
        ChatRequest()  # type: ignore[call-arg]


def test_chat_response_defaults():
    resp = ChatResponse(response="test")
    assert resp.confidence == 0.0
    assert resp.citations == []
    assert resp.compliance_data is None


def test_compliance_rule_valid():
    rule = ComplianceRule(
        rule_id="R1",
        category="data_governance",
        requirement="Must have retention policy",
        regulation_source="EO_N-5-26",
        severity="critical",
    )
    assert rule.regulation_source == "EO_N-5-26"


def test_compliance_rule_invalid_source():
    with pytest.raises(ValidationError):
        ComplianceRule(
            rule_id="R1",
            category="data_governance",
            requirement="test",
            regulation_source="INVALID",
            severity="critical",
        )


def test_compliance_score_valid():
    score = ComplianceScore(
        overall_score=85.0,
        risk_classification="low",
        compliant_count=15,
        non_compliant_count=1,
        partial_count=2,
    )
    assert score.overall_score == 85.0


def test_compliance_score_out_of_range():
    with pytest.raises(ValidationError):
        ComplianceScore(overall_score=150.0)


def test_compliance_result_valid():
    result = ComplianceResult(
        rule_id="R1",
        status="compliant",
        evidence="Verified",
    )
    assert result.confidence == 0.0


def test_compliance_result_invalid_status():
    with pytest.raises(ValidationError):
        ComplianceResult(
            rule_id="R1",
            status="unknown",
            evidence="test",
        )


def test_attestation_document_defaults():
    doc = AttestationDocument(doc_id="D1", vendor_name="Test Corp")
    assert doc.file_type == "pdf"
    assert doc.status == "pending"


def test_compliance_gap_valid():
    gap = ComplianceGap(
        rule_id="R1",
        category="bias_testing",
        requirement="Must have bias testing",
        severity="high",
        remediation_guidance="Conduct testing",
        estimated_effort="medium",
    )
    assert gap.estimated_effort == "medium"


def test_risk_classification_valid():
    risk = RiskClassification(tier=2, classification="Medium", justification="Based on score")
    assert risk.tier == 2


def test_risk_classification_invalid_tier():
    with pytest.raises(ValidationError):
        RiskClassification(tier=5, classification="Test", justification="Test")


def test_routing_decision_valid():
    rd = RoutingDecision(department="compliance_review", priority="high", reason="test")
    assert rd.escalate is False


def test_routing_decision_invalid_priority():
    with pytest.raises(ValidationError):
        RoutingDecision(department="test", priority="urgent", reason="test")


def test_citation_valid():
    c = Citation(source="EO N-5-26", text="Test", regulation="EO_N-5-26")
    assert c.regulation == "EO_N-5-26"


def test_gap_analysis_empty():
    ga = GapAnalysis()
    assert ga.gaps == []


def test_compliance_query_defaults():
    q = ComplianceQuery(raw_input="test")
    assert q.intent == "compliance_check"
    assert q.entities == {}
