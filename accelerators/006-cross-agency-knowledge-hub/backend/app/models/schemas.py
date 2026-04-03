"""Pydantic v2 models for Cross-Agency Knowledge Hub."""

from datetime import datetime
from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    text: str
    agency: str | None = None
    document_id: str | None = None


class DocumentResult(BaseModel):
    doc_id: str
    title: str
    agency: str
    department: str
    document_type: str  # policy/procedure/regulation/guidance/memo/faq
    summary: str
    relevance_score: float
    last_updated: datetime
    access_level: str = "public"  # public/internal/restricted


class CrossReference(BaseModel):
    source_doc_id: str
    target_doc_id: str
    relationship: str  # supersedes/cites/complements/conflicts
    description: str


class ExpertInfo(BaseModel):
    expert_id: str
    name: str
    agency: str
    department: str
    expertise_areas: list[str] = Field(default_factory=list)
    email: str
    available: bool = True


class AgencyPermission(BaseModel):
    agency_code: str
    agency_name: str
    access_level: str
    departments: list[str] = Field(default_factory=list)


class SearchQuery(BaseModel):
    raw_input: str
    intent: str
    agencies: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    document_types: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    session_id: str | None = None
    agency_filter: list[str] | None = None
    document_types: list[str] | None = None


class ChatResponse(BaseModel):
    response: str
    confidence: float
    citations: list[Citation] = Field(default_factory=list)
    documents: list[DocumentResult] | None = None
    experts: list[ExpertInfo] | None = None
    cross_references: list[CrossReference] | None = None


class AgentResponse(BaseModel):
    intent: str
    response_text: str
    confidence: float
    citations: list[Citation] = Field(default_factory=list)
    data: dict | None = None


class RoutingDecision(BaseModel):
    department: str
    priority: str
    reason: str
    escalate: bool = False
