"""Pydantic v2 models for BenefitsCal Navigator."""

from pydantic import BaseModel, Field


class BenefitQuery(BaseModel):
    raw_input: str
    intent: str = "eligibility_check"
    program: str | None = None
    language: str = "en"
    entities: dict = Field(default_factory=dict)
    pii_detected: bool = False


class ProgramInfo(BaseModel):
    program_id: str
    name: str
    description: str
    eligibility_url: str
    agency: str = "CDSS"


class EligibilityResult(BaseModel):
    program: str
    eligible: bool | None = None
    summary: str
    citations: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    language: str = "en"
