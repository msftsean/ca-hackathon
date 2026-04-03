"""Pydantic v2 models for Medi-Cal Eligibility Agent."""

from datetime import datetime
from pydantic import BaseModel, Field


# --- Request / Response ---

class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    session_id: str | None = None
    application_id: str | None = None


class Citation(BaseModel):
    source: str
    text: str
    regulation_ref: str | None = None


class EligibilityScreening(BaseModel):
    program_type: str  # MAGI_Adult, MAGI_Child, ABD, QMB, SLMB, Pregnancy
    likely_eligible: bool
    confidence: float
    income_limit: float
    fpl_percentage: float
    factors: list[str] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class ApplicationStatus(BaseModel):
    app_id: str
    status: str
    last_updated: datetime
    next_action: str | None = None


class ChatResponse(BaseModel):
    response: str
    confidence: float
    citations: list[Citation] = Field(default_factory=list)
    eligibility: EligibilityScreening | None = None
    application: ApplicationStatus | None = None


# --- Internal Agent Models ---

class MediCalQuery(BaseModel):
    raw_input: str
    intent: str = "general_info"
    entities: dict = Field(default_factory=dict)
    program_type: str | None = None


class ApplicationInfo(BaseModel):
    app_id: str
    applicant_name: str
    household_size: int
    monthly_income: float
    county: str
    status: str = "draft"  # draft/submitted/pending_verification/approved/denied/pending_documents
    created_at: datetime = Field(default_factory=datetime.utcnow)
    program_type: str = "MAGI_Adult"


class DocumentInfo(BaseModel):
    doc_id: str
    doc_type: str  # W2, paystub, form_1040, SSA_1099, bank_statement
    upload_status: str = "pending"  # pending/uploaded/verified/rejected
    extracted_data: dict | None = None


class IncomeVerification(BaseModel):
    source: str
    amount: float
    frequency: str = "monthly"  # monthly/annual/biweekly
    verified: bool = False


class RoutingDecision(BaseModel):
    destination: str
    priority: str = "medium"
    escalate: bool = False
    escalation_reason: str | None = None


class AgentResponse(BaseModel):
    response: str
    confidence: float = 0.0
    citations: list[Citation] = Field(default_factory=list)
    eligibility: EligibilityScreening | None = None
    application: ApplicationStatus | None = None
