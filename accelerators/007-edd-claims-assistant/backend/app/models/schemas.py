"""Pydantic v2 models for EDD Claims Assistant."""

from datetime import date
from pydantic import BaseModel, Field


class ClaimQuery(BaseModel):
    raw_input: str
    intent: str = "status_check"
    claim_id: str | None = None
    program: str | None = None  # ui, di, pfl
    pii_detected: bool = False


class ClaimStatus(BaseModel):
    claim_id: str
    program: str  # ui, di, pfl
    status: str  # pending, approved, denied, in_review, paid
    claimant_name: str | None = None
    filed_date: date | None = None
    weekly_benefit_amount: float | None = None
    last_payment_date: date | None = None
    next_certification_date: date | None = None
    notes: list[str] = Field(default_factory=list)


class EligibilityScreening(BaseModel):
    program: str
    likely_eligible: bool
    reason: str
    requirements: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class SupportTicket(BaseModel):
    ticket_id: str
    claim_id: str | None = None
    category: str
    description: str
    priority: str = "normal"  # low, normal, high, urgent
    status: str = "open"
    created_at: date | None = None
