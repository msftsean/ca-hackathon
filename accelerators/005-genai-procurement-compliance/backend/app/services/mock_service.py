"""Mock service returning sample compliance evaluation data."""

from datetime import datetime
from app.models.schemas import ComplianceQuery, ComplianceReport, FrameworkScore


class MockComplianceService:
    """Returns mock compliance evaluation results for development."""

    def evaluate_compliance(self, query: ComplianceQuery, frameworks: list[str]) -> ComplianceReport:
        scores = []
        for fw in frameworks:
            if fw == "eo-n-5-26":
                scores.append(FrameworkScore(
                    framework_id="eo-n-5-26",
                    framework_name="Executive Order N-5-26",
                    score=0.72,
                    findings=["AI model architecture not fully disclosed", "Bias testing report incomplete"],
                    remediation=["Submit complete model card", "Provide demographic bias test results"],
                    status="needs_remediation",
                ))
            elif fw == "sb-53":
                scores.append(FrameworkScore(
                    framework_id="sb-53",
                    framework_name="SB 53 — AI Safety",
                    score=0.85,
                    findings=["Safety evaluation documentation provided"],
                    remediation=[],
                    status="passed",
                ))
            elif fw == "simm-5300":
                scores.append(FrameworkScore(
                    framework_id="simm-5300",
                    framework_name="SIMM 5300 — IT Procurement",
                    score=0.68,
                    findings=["Data handling policy missing retention schedule"],
                    remediation=["Add data retention and disposal procedures"],
                    status="needs_remediation",
                ))

        overall = sum(s.score for s in scores) / len(scores) if scores else 0.0
        risk = "low" if overall >= 0.8 else "medium" if overall >= 0.6 else "high"

        return ComplianceReport(
            attestation_id=query.attestation_id or "ATT-2025-MOCK-001",
            vendor_name=query.vendor_name or "Mock Vendor Inc.",
            overall_score=round(overall, 2),
            risk_level=risk,
            framework_scores=scores,
            recommendation="Conditional approval pending remediation of identified gaps." if risk == "medium" else "Approved" if risk == "low" else "Further review required.",
            reviewed_at=datetime.now(),
        )
