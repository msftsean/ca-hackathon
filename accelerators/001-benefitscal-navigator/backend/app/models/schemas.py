"""Pydantic v2 models for BenefitsCal Navigator."""

from datetime import datetime
from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    text: str
    policy_ref: str | None = None
    url: str | None = None


class ProgramInfo(BaseModel):
    program_id: str
    name: str
    description: str
    agency: str
    requirements: list[str] = Field(default_factory=list)
    documents_needed: list[str] = Field(default_factory=list)


class EligibilityResult(BaseModel):
    program: str
    likely_eligible: bool
    confidence: float
    factors: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class LanguagePreference(BaseModel):
    code: str
    name: str
    supported: bool


class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    session_id: str | None = None
    county: str | None = None


class ChatResponse(BaseModel):
    response: str
    confidence: float
    citations: list[Citation] = Field(default_factory=list)
    programs: list[ProgramInfo] | None = None
    eligibility: EligibilityResult | None = None


class BenefitQuery(BaseModel):
    raw_input: str
    intent: str
    language: str = "en"
    entities: dict = Field(default_factory=dict)
    county: str | None = None
    program: str | None = None


class AgentResponse(BaseModel):
    intent: str
    response_text: str
    confidence: float
    citations: list[Citation] = Field(default_factory=list)
    data: dict | None = None


class RoutingDecision(BaseModel):
    department: str
    priority: str  # low/medium/high/critical
    reason: str
    escalate: bool = False


class EscalationTicket(BaseModel):
    ticket_id: str
    reason: str
    priority: str
    created_at: datetime
