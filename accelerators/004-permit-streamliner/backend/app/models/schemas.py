"""Pydantic v2 models for Permit Streamliner."""

from datetime import date, datetime
from pydantic import BaseModel, Field


class PermitQuery(BaseModel):
    raw_input: str
    intent: str = "permit_inquiry"
    permit_type: str | None = None
    jurisdiction: str | None = None
    entities: dict = Field(default_factory=dict)


class ChecklistItem(BaseModel):
    item_id: str
    description: str
    required: bool = True
    completed: bool = False
    document_type: str | None = None


class PermitApplication(BaseModel):
    permit_id: str
    permit_type: str  # residential, commercial, adu, solar, demolition
    applicant_name: str
    jurisdiction: str  # opr, hcd, dca
    status: str = "intake"  # intake, review, approved, denied, revision_needed
    submitted_date: date | None = None
    sla_deadline: date | None = None
    sla_days_remaining: int | None = None
    checklist: list[ChecklistItem] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class SLATracking(BaseModel):
    permit_id: str
    sla_start: datetime
    sla_target_days: int = 30
    days_elapsed: int = 0
    on_track: bool = True
    blockers: list[str] = Field(default_factory=list)
