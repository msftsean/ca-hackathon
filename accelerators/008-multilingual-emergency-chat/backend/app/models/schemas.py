"""Pydantic v2 models for Multilingual Emergency Chatbot."""

from datetime import datetime
from pydantic import BaseModel, Field


class EmergencyQuery(BaseModel):
    raw_input: str
    intent: str = "general_info"
    language: str = "en"
    location: str | None = None
    emergency_type: str | None = None  # wildfire, earthquake, flood, tsunami


class EmergencyAlert(BaseModel):
    alert_id: str
    title: str
    description: str
    severity: str  # extreme, severe, moderate, minor
    emergency_type: str
    affected_areas: list[str] = Field(default_factory=list)
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    instructions: str = ""
    source: str = "Cal OES"


class ShelterInfo(BaseModel):
    shelter_id: str
    name: str
    address: str
    city: str
    county: str
    capacity: int
    current_occupancy: int = 0
    accepts_pets: bool = False
    ada_accessible: bool = True
    status: str = "open"  # open, full, closed


class TranslatedMessage(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    sms_compatible: bool = True
    character_count: int = 0
