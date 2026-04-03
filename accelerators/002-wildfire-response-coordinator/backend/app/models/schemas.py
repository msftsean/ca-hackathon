"""Pydantic v2 models for Wildfire Response Coordinator."""

from datetime import datetime
from pydantic import BaseModel, Field


class IncidentQuery(BaseModel):
    raw_input: str
    intent: str = "situation_report"
    incident_id: str | None = None
    region: str | None = None
    entities: dict = Field(default_factory=dict)


class WildfireIncident(BaseModel):
    incident_id: str
    name: str
    location: str
    county: str
    acres_burned: float
    containment_pct: float
    status: str = "active"
    latitude: float | None = None
    longitude: float | None = None
    started_at: datetime | None = None
    updated_at: datetime | None = None


class ResourceAllocation(BaseModel):
    resource_id: str
    resource_type: str  # engine, crew, aircraft, dozer
    assigned_incident: str
    status: str = "available"
    quantity: int = 1
    eta_minutes: int | None = None


class EvacuationZone(BaseModel):
    zone_id: str
    name: str
    level: str  # warning, order, shelter-in-place
    population_affected: int
    routes: list[str] = Field(default_factory=list)
    shelters: list[str] = Field(default_factory=list)
