"""Pydantic v2 models for GenAI Procurement Compliance."""

from datetime import datetime
from pydantic import BaseModel, Field


class ComplianceQuery(BaseModel):
    raw_input: str
    intent: str = "compliance_review"
    attestation_id: str | None = None
    vendor_name: str | None = None
    frameworks: list[str] = Field(default_factory=lambda: ["eo-n-5-26", "sb-53"])


class FrameworkScore(BaseModel):
    framework_id: str
    framework_name: str
    score: float  # 0.0 to 1.0
    max_score: float = 1.0
    findings: list[str] = Field(default_factory=list)
    remediation: list[str] = Field(default_factory=list)
    status: str = "reviewed"  # reviewed, passed, failed, needs_remediation


class VendorAttestation(BaseModel):
    attestation_id: str
    vendor_name: str
    product_name: str
    submission_date: datetime | None = None
    ai_model_disclosed: bool = False
    training_data_disclosed: bool = False
    bias_testing_completed: bool = False
    security_assessment_completed: bool = False
    data_handling_policy: str | None = None


class ComplianceReport(BaseModel):
    attestation_id: str
    vendor_name: str
    overall_score: float
    risk_level: str  # low, medium, high, critical
    framework_scores: list[FrameworkScore] = Field(default_factory=list)
    recommendation: str
    reviewed_at: datetime | None = None
