"""Pydantic v2 models for Cross-Agency Knowledge Hub."""

from datetime import datetime
from pydantic import BaseModel, Field


class KnowledgeQuery(BaseModel):
    raw_input: str
    intent: str = "search"
    topic: str | None = None
    agency_scope: str = "all"
    search_mode: str = "hybrid"  # bm25, semantic, hybrid


class SearchResult(BaseModel):
    document_id: str
    title: str
    snippet: str
    source_agency: str
    document_type: str  # policy, procedure, memo, guideline, form
    url: str | None = None
    relevance_score: float = 0.0
    last_updated: datetime | None = None


class PolicyDocument(BaseModel):
    document_id: str
    title: str
    agency: str
    category: str
    content: str
    effective_date: datetime | None = None
    expiration_date: datetime | None = None
    access_level: str = "public"  # public, internal, confidential
    tags: list[str] = Field(default_factory=list)


class AgencyScope(BaseModel):
    agency_code: str
    agency_name: str
    index_name: str
    document_count: int = 0
    last_indexed: datetime | None = None
