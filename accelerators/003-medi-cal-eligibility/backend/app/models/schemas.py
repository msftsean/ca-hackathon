"""Pydantic v2 models for Medi-Cal Eligibility Agent."""

from datetime import date
from pydantic import BaseModel, Field


class EligibilityQuery(BaseModel):
    raw_input: str
    intent: str = "eligibility_check"
    document_ids: list[str] = Field(default_factory=list)
    applicant_info: dict = Field(default_factory=dict)
    pii_detected: bool = False


class IncomeRecord(BaseModel):
    source: str  # employment, self-employment, social-security, etc.
    document_type: str  # w2, pay_stub, tax_return, ssi_statement
    gross_amount: float
    period: str  # monthly, annual
    employer: str | None = None
    verified: bool = False
    extracted_at: date | None = None


class MediCalApplication(BaseModel):
    application_id: str
    applicant_name: str
    household_size: int
    county: str
    income_records: list[IncomeRecord] = Field(default_factory=list)
    total_monthly_income: float = 0.0
    application_date: date | None = None
    status: str = "pending"


class EligibilityDetermination(BaseModel):
    application_id: str
    eligible: bool
    program: str  # medi-cal, medi-cal-expansion, covered-california
    magi_income: float
    fpl_percentage: float
    income_limit: float
    household_size: int
    determination_reason: str
    next_steps: list[str] = Field(default_factory=list)
    confidence: float = 0.0
