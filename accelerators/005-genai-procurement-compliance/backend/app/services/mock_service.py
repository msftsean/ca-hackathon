"""Comprehensive mock data for GenAI Procurement Compliance."""

from datetime import datetime

from app.models.schemas import (
    AttestationDocument,
    ComplianceGap,
    ComplianceResult,
    ComplianceRule,
    ComplianceScore,
    GapAnalysis,
    RiskClassification,
)


class MockComplianceService:
    """Provides mock compliance data for development and testing."""

    def __init__(self) -> None:
        self._rules = self._build_rules()
        self._vendor_profiles = self._build_vendor_profiles()

    # ---- compliance rules -----------------------------------------------

    def get_rules(self) -> list[ComplianceRule]:
        return self._rules

    def _build_rules(self) -> list[ComplianceRule]:
        return [
            ComplianceRule(rule_id="DG-001", category="data_governance", requirement="Data retention policy with defined disposal schedule", regulation_source="EO_N-5-26", severity="critical"),
            ComplianceRule(rule_id="DG-002", category="data_governance", requirement="Data residency within US boundaries", regulation_source="EO_N-5-26", severity="high"),
            ComplianceRule(rule_id="DG-003", category="data_governance", requirement="Third-party data sharing restrictions", regulation_source="EO_N-5-26", severity="high"),
            ComplianceRule(rule_id="MT-001", category="model_transparency", requirement="AI model architecture disclosure", regulation_source="SB_53", severity="critical"),
            ComplianceRule(rule_id="MT-002", category="model_transparency", requirement="Training data sources documented", regulation_source="SB_53", severity="high"),
            ComplianceRule(rule_id="MT-003", category="model_transparency", requirement="Model performance metrics published", regulation_source="NIST_AI_RMF", severity="medium"),
            ComplianceRule(rule_id="BT-001", category="bias_testing", requirement="Demographic parity testing completed", regulation_source="NIST_AI_RMF", severity="critical"),
            ComplianceRule(rule_id="BT-002", category="bias_testing", requirement="Equalized odds evaluation", regulation_source="NIST_AI_RMF", severity="high"),
            ComplianceRule(rule_id="BT-003", category="bias_testing", requirement="Language accuracy across supported languages", regulation_source="SB_53", severity="medium"),
            ComplianceRule(rule_id="PP-001", category="privacy_protection", requirement="CCPA/CPRA compliance certification", regulation_source="EO_N-5-26", severity="critical"),
            ComplianceRule(rule_id="PP-002", category="privacy_protection", requirement="PII detection and masking capabilities", regulation_source="EO_N-5-26", severity="high"),
            ComplianceRule(rule_id="PP-003", category="privacy_protection", requirement="Data minimization practices", regulation_source="NIST_AI_RMF", severity="medium"),
            ComplianceRule(rule_id="HO-001", category="human_oversight", requirement="Human-in-the-loop for high-risk decisions", regulation_source="SB_53", severity="critical"),
            ComplianceRule(rule_id="HO-002", category="human_oversight", requirement="Override mechanism for AI outputs", regulation_source="SB_53", severity="high"),
            ComplianceRule(rule_id="HO-003", category="human_oversight", requirement="Escalation procedures documented", regulation_source="NIST_AI_RMF", severity="medium"),
            ComplianceRule(rule_id="IR-001", category="incident_response", requirement="AI incident response plan", regulation_source="EO_N-5-26", severity="high"),
            ComplianceRule(rule_id="IR-002", category="incident_response", requirement="Incident reporting timeline (72 hours)", regulation_source="SB_53", severity="critical"),
            ComplianceRule(rule_id="IR-003", category="incident_response", requirement="Post-incident review process", regulation_source="NIST_AI_RMF", severity="medium"),
        ]

    # ---- vendor profiles ------------------------------------------------

    def _build_vendor_profiles(self) -> dict[str, dict]:
        return {
            "AI Solutions Corp": {
                "score": 92.0,
                "risk": "low",
                "tier": 1,
                "compliant": 15,
                "non_compliant": 1,
                "partial": 2,
                "categories": {
                    "data_governance": 95.0,
                    "model_transparency": 88.0,
                    "bias_testing": 92.0,
                    "privacy_protection": 96.0,
                    "human_oversight": 90.0,
                    "incident_response": 91.0,
                },
                "gaps": [
                    ComplianceGap(rule_id="MT-002", category="model_transparency", requirement="Training data sources documented", severity="high", remediation_guidance="Submit complete training data provenance documentation", estimated_effort="medium"),
                    ComplianceGap(rule_id="BT-003", category="bias_testing", requirement="Language accuracy across supported languages", severity="medium", remediation_guidance="Add multilingual accuracy testing results", estimated_effort="low"),
                ],
            },
            "GovTech Analytics": {
                "score": 71.0,
                "risk": "medium",
                "tier": 2,
                "compliant": 10,
                "non_compliant": 4,
                "partial": 4,
                "categories": {
                    "data_governance": 80.0,
                    "model_transparency": 45.0,
                    "bias_testing": 50.0,
                    "privacy_protection": 85.0,
                    "human_oversight": 78.0,
                    "incident_response": 72.0,
                },
                "gaps": [
                    ComplianceGap(rule_id="MT-001", category="model_transparency", requirement="AI model architecture disclosure", severity="critical", remediation_guidance="Disclose full model architecture and capabilities", estimated_effort="high"),
                    ComplianceGap(rule_id="MT-002", category="model_transparency", requirement="Training data sources documented", severity="high", remediation_guidance="Provide training data documentation", estimated_effort="high"),
                    ComplianceGap(rule_id="BT-001", category="bias_testing", requirement="Demographic parity testing completed", severity="critical", remediation_guidance="Conduct and submit demographic parity testing", estimated_effort="high"),
                    ComplianceGap(rule_id="BT-002", category="bias_testing", requirement="Equalized odds evaluation", severity="high", remediation_guidance="Complete equalized odds evaluation", estimated_effort="medium"),
                    ComplianceGap(rule_id="IR-001", category="incident_response", requirement="AI incident response plan", severity="high", remediation_guidance="Develop and submit incident response plan", estimated_effort="medium"),
                ],
            },
            "California Data Systems": {
                "score": 45.0,
                "risk": "high",
                "tier": 3,
                "compliant": 6,
                "non_compliant": 8,
                "partial": 4,
                "categories": {
                    "data_governance": 60.0,
                    "model_transparency": 30.0,
                    "bias_testing": 25.0,
                    "privacy_protection": 55.0,
                    "human_oversight": 40.0,
                    "incident_response": 35.0,
                },
                "gaps": [
                    ComplianceGap(rule_id="DG-001", category="data_governance", requirement="Data retention policy with defined disposal schedule", severity="critical", remediation_guidance="Create data retention and disposal policy", estimated_effort="high"),
                    ComplianceGap(rule_id="MT-001", category="model_transparency", requirement="AI model architecture disclosure", severity="critical", remediation_guidance="Disclose model architecture", estimated_effort="high"),
                    ComplianceGap(rule_id="BT-001", category="bias_testing", requirement="Demographic parity testing completed", severity="critical", remediation_guidance="Conduct bias testing", estimated_effort="high"),
                    ComplianceGap(rule_id="PP-001", category="privacy_protection", requirement="CCPA/CPRA compliance certification", severity="critical", remediation_guidance="Obtain CCPA/CPRA compliance certification", estimated_effort="high"),
                    ComplianceGap(rule_id="HO-001", category="human_oversight", requirement="Human-in-the-loop for high-risk decisions", severity="critical", remediation_guidance="Implement human oversight for high-risk decisions", estimated_effort="high"),
                    ComplianceGap(rule_id="IR-002", category="incident_response", requirement="Incident reporting timeline (72 hours)", severity="critical", remediation_guidance="Establish 72-hour incident reporting process", estimated_effort="medium"),
                ],
            },
        }

    # ---- public methods -------------------------------------------------

    def get_compliance_score(self, vendor_name: str | None = None) -> ComplianceScore:
        profile = self._get_profile(vendor_name)
        return ComplianceScore(
            overall_score=profile["score"],
            category_scores=profile["categories"],
            risk_classification=profile["risk"],
            compliant_count=profile["compliant"],
            non_compliant_count=profile["non_compliant"],
            partial_count=profile["partial"],
        )

    def get_gap_analysis(self, vendor_name: str | None = None) -> GapAnalysis:
        profile = self._get_profile(vendor_name)
        return GapAnalysis(gaps=profile["gaps"])

    def get_risk_classification(self, vendor_name: str | None = None) -> RiskClassification:
        profile = self._get_profile(vendor_name)
        classifications = {
            1: "Low Risk — Approved for deployment",
            2: "Medium Risk — Conditional approval with monitoring",
            3: "High Risk — Requires remediation before approval",
            4: "Critical Risk — Rejected, fundamental deficiencies",
        }
        tier = profile["tier"]
        return RiskClassification(
            tier=tier,
            classification=classifications.get(tier, "Unknown"),
            justification=f"Based on overall compliance score of {profile['score']}/100 with {profile['non_compliant']} non-compliant rules",
        )

    def get_all_vendor_scores(self) -> dict[str, ComplianceScore]:
        return {name: self.get_compliance_score(name) for name in self._vendor_profiles}

    def create_attestation(self) -> AttestationDocument:
        return AttestationDocument(
            doc_id="ATT-2025-MOCK-001",
            vendor_name="Uploaded Vendor",
            upload_date=datetime.now(),
            file_type="pdf",
            status="analyzing",
        )

    def get_compliance_results(self, vendor_name: str | None = None) -> list[ComplianceResult]:
        profile = self._get_profile(vendor_name)
        gap_rule_ids = {g.rule_id for g in profile["gaps"]}
        results = []
        for rule in self._rules:
            if rule.rule_id in gap_rule_ids:
                status = "non_compliant"
                evidence = "Gap identified during review"
                confidence = 0.85
            else:
                status = "compliant"
                evidence = "Attestation documentation verified"
                confidence = 0.92
            results.append(ComplianceResult(
                rule_id=rule.rule_id,
                status=status,
                evidence=evidence,
                confidence=confidence,
            ))
        return results

    def _get_profile(self, vendor_name: str | None) -> dict:
        if vendor_name and vendor_name in self._vendor_profiles:
            return self._vendor_profiles[vendor_name]
        return self._vendor_profiles["GovTech Analytics"]
