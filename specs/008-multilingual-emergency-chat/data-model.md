# Data Model: Multilingual Emergency Chatbot (008-multilingual-emergency-chat)

**Phase**: 1 — Entity definitions  
**Author**: Mouse (Tester/Spec Creator)  
**Date**: 2026-04-02  
**Feature**: Real-time emergency information in 70+ languages with SMS access

Patterns follow the existing codebase:
- **Backend**: Pydantic v2 with `Field(...)`, `field_validator`, `Literal` types — matches `backend/app/models/schemas.py`
- **Enums**: `str, Enum` subclasses — matches `backend/app/models/enums.py`
- **Frontend**: TypeScript interfaces and `enum` — matches `frontend/src/` conventions

---

## Backend Entities — Pydantic v2

### Enumerations

```python
# backend/app/models/emergency_enums.py

from enum import Enum


class AlertType(str, Enum):
    """Type of emergency alert."""
    FIRE = "fire"
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    AIR_QUALITY = "air_quality"
    EVACUATION = "evacuation"
    WEATHER = "weather"
    HAZMAT = "hazmat"
    TSUNAMI = "tsunami"
    POWER_OUTAGE = "power_outage"


class Severity(str, Enum):
    """Alert severity level following EAS (Emergency Alert System) standards."""
    ADVISORY = "advisory"      # Informational
    WARNING = "warning"        # Take action
    URGENT = "urgent"          # Immediate action required
    EXTREME = "extreme"        # Life-threatening


class EvacuationStatus(str, Enum):
    """Evacuation order type."""
    NO_ORDER = "no_order"
    VOLUNTARY = "voluntary"
    MANDATORY = "mandatory"


class ShelterServiceType(str, Enum):
    """Services available at a shelter."""
    ADA_ACCESSIBLE = "ada_accessible"
    PETS_ALLOWED = "pets_allowed"
    MEDICAL_CLINIC = "medical_clinic"
    MENTAL_HEALTH = "mental_health"
    FOOD_SERVICE = "food_service"
    CHARGING_STATIONS = "charging_stations"
    TRANSPORTATION = "transportation"


class AQICategory(str, Enum):
    """Air Quality Index health risk categories (EPA standard)."""
    GOOD = "good"                      # 0-50
    MODERATE = "moderate"              # 51-100
    UNHEALTHY_SENSITIVE = "unhealthy_sensitive"  # 101-150
    UNHEALTHY = "unhealthy"            # 151-200
    VERY_UNHEALTHY = "very_unhealthy"  # 201-300
    HAZARDOUS = "hazardous"            # 301+
```

---

### EmergencyAlert

Represents an active emergency alert for a specific area.

```python
# backend/app/models/emergency_schemas.py

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class EmergencyAlert(BaseModel):
    """Active emergency alert (fire, flood, earthquake, air quality, etc.)."""

    alert_id: str = Field(..., description="Unique alert identifier")
    type: AlertType = Field(..., description="Type of emergency")
    severity: Severity = Field(..., description="Severity level")
    area: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Affected area (ZIP codes, counties, neighborhoods, or coordinates)"
    )
    title: str = Field(..., min_length=1, max_length=200, description="Alert title")
    message: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Detailed alert message"
    )
    issued_at: datetime = Field(..., description="When alert was issued")
    expires_at: Optional[datetime] = Field(None, description="When alert expires (None = until further notice)")
    source: str = Field(..., description="Issuing agency (e.g., 'Cal OES', 'National Weather Service')")
    affected_zip_codes: List[str] = Field(
        default_factory=list,
        description="List of affected ZIP codes for fast location matching"
    )
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    @field_validator("affected_zip_codes")
    @classmethod
    def validate_zip_codes(cls, v: List[str]) -> List[str]:
        """Ensure ZIP codes are 5 digits."""
        for zip_code in v:
            if not zip_code.isdigit() or len(zip_code) != 5:
                raise ValueError(f"Invalid ZIP code: {zip_code}")
        return v
```

---

### EvacuationOrder

Tracks evacuation orders for specific zones.

```python
class EvacuationOrder(BaseModel):
    """Evacuation order for a specific area or zone."""

    order_id: str = Field(..., description="Unique order identifier")
    zone: str = Field(..., description="Evacuation zone or area name")
    status: EvacuationStatus = Field(..., description="Evacuation order type")
    issued_at: datetime = Field(..., description="When order was issued")
    expires_at: Optional[datetime] = Field(None, description="When order expires (None = until further notice)")
    affected_zip_codes: List[str] = Field(
        default_factory=list,
        description="ZIP codes in this evacuation zone"
    )
    affected_addresses: List[str] = Field(
        default_factory=list,
        description="Specific addresses or streets (if granular)"
    )
    recommended_routes: List[str] = Field(
        default_factory=list,
        description="Recommended evacuation routes (e.g., 'Highway 1 South', 'PCH Northbound')"
    )
    road_closures: List[str] = Field(
        default_factory=list,
        description="Closed roads or routes to avoid"
    )
    shelter_ids: List[str] = Field(
        default_factory=list,
        description="IDs of recommended shelters for this zone"
    )
    instructions: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Additional instructions (e.g., 'Bring medications, pet supplies')"
    )
    source: str = Field(..., description="Issuing authority (e.g., 'LA County Fire Dept', 'Cal OES')")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
```

---

### Shelter

Emergency shelter with capacity and services.

```python
class Shelter(BaseModel):
    """Emergency shelter location with capacity and services."""

    shelter_id: str = Field(..., description="Unique shelter identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Shelter name")
    address: str = Field(..., description="Full street address")
    city: str = Field(..., description="City")
    zip_code: str = Field(..., description="ZIP code")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude for distance calculation")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude for distance calculation")
    capacity_current: int = Field(..., ge=0, description="Current occupancy")
    capacity_max: int = Field(..., ge=1, description="Maximum capacity")
    is_at_capacity: bool = Field(default=False, description="True if shelter is full")
    services: List[ShelterServiceType] = Field(
        default_factory=list,
        description="Available services (ADA, pets, medical, etc.)"
    )
    hours: str = Field(
        default="24/7",
        description="Operating hours (e.g., '24/7', '8am-8pm')"
    )
    contact_phone: str = Field(..., description="Contact phone number")
    contact_email: Optional[str] = Field(None, description="Contact email")
    notes: str = Field(
        default="",
        max_length=500,
        description="Additional notes (e.g., 'Crate required for pets', 'ID verification needed')"
    )
    capacity_last_updated: datetime = Field(
        ...,
        description="When capacity was last updated (critical for accurate info)"
    )
    is_open: bool = Field(default=True, description="False if shelter is closed")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, v: str) -> str:
        """Ensure ZIP code is 5 digits."""
        if not v.isdigit() or len(v) != 5:
            raise ValueError(f"Invalid ZIP code: {v}")
        return v
```

---

### AirQualityReport

Air quality data with AQI and pollutant breakdown.

```python
class AirQualityReport(BaseModel):
    """Air quality data for a specific location."""

    location: str = Field(..., description="Location name (city, neighborhood, or monitoring station)")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    aqi: int = Field(..., ge=0, le=500, description="Air Quality Index (0-500)")
    category: AQICategory = Field(..., description="Health risk category")
    pm25: Optional[float] = Field(None, ge=0, description="PM2.5 concentration (µg/m³)")
    pm10: Optional[float] = Field(None, ge=0, description="PM10 concentration (µg/m³)")
    ozone: Optional[float] = Field(None, ge=0, description="Ozone concentration (ppb)")
    health_guidance: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Health recommendations based on AQI category"
    )
    forecast: Optional[str] = Field(
        None,
        max_length=500,
        description="24-hour AQI forecast (if available)"
    )
    monitoring_station: str = Field(..., description="Name of monitoring station providing this data")
    updated_at: datetime = Field(..., description="When this data was collected")
    source: str = Field(default="PurpleAir / AirNow", description="Data source")

    @field_validator("aqi")
    @classmethod
    def validate_aqi(cls, v: int) -> int:
        """Ensure AQI is within valid range."""
        if v < 0 or v > 500:
            raise ValueError("AQI must be between 0 and 500")
        return v
```

---

### TranslationCache

Caches translated content to reduce Azure Translator API calls.

```python
class TranslationCache(BaseModel):
    """Translation cache entry."""

    content_hash: str = Field(
        ...,
        min_length=32,
        max_length=32,
        description="MD5 hash of source content"
    )
    source_language: str = Field(..., description="Source language code (e.g., 'en')")
    target_language: str = Field(..., description="Target language code (e.g., 'es', 'zh-Hans', 'vi')")
    translated_text: str = Field(..., min_length=1, description="Translated content")
    cached_at: datetime = Field(default_factory=datetime.utcnow, description="When this was cached")
    hit_count: int = Field(default=0, ge=0, description="Number of times this cache entry was used")

    @field_validator("content_hash")
    @classmethod
    def validate_hash(cls, v: str) -> str:
        """Ensure hash is 32-character MD5."""
        if len(v) != 32:
            raise ValueError("content_hash must be 32-character MD5 hash")
        return v
```

---

### SMSSession

Tracks SMS interactions for conversation continuity.

```python
class SMSMessage(BaseModel):
    """A single SMS message in a conversation."""

    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, max_length=1600, description="Message text")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SMSSession(BaseModel):
    """SMS conversation session."""

    session_id: str = Field(..., description="Unique session identifier")
    phone_hash: str = Field(
        ...,
        description="Hashed phone number (SHA-256) for privacy"
    )
    language: str = Field(default="en", description="Selected language code")
    last_message: Optional[str] = Field(None, description="Last message for context")
    location: Optional[str] = Field(None, description="Last queried location (ZIP or address)")
    messages: List[SMSMessage] = Field(
        default_factory=list,
        description="Message history (limited to last 10 for performance)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Session expiration (default: 1 hour)")
```

---

### Location

Represents a California location for alert/shelter lookups.

```python
class Location(BaseModel):
    """A geographic location in California."""

    address: Optional[str] = Field(None, description="Full street address")
    zip_code: str = Field(..., description="5-digit ZIP code")
    city: Optional[str] = Field(None, description="City name")
    county: Optional[str] = Field(None, description="County name")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    alert_zones: List[str] = Field(
        default_factory=list,
        description="Associated alert zones for rapid alert lookup"
    )

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, v: str) -> str:
        """Ensure ZIP code is 5 digits."""
        if not v.isdigit() or len(v) != 5:
            raise ValueError(f"Invalid ZIP code: {v}")
        return v
```

---

## Frontend Entities — TypeScript

### Enumerations

```typescript
// frontend/src/types/emergency.ts

export enum AlertType {
  FIRE = 'fire',
  FLOOD = 'flood',
  EARTHQUAKE = 'earthquake',
  AIR_QUALITY = 'air_quality',
  EVACUATION = 'evacuation',
  WEATHER = 'weather',
  HAZMAT = 'hazmat',
  TSUNAMI = 'tsunami',
  POWER_OUTAGE = 'power_outage',
}

export enum Severity {
  ADVISORY = 'advisory',
  WARNING = 'warning',
  URGENT = 'urgent',
  EXTREME = 'extreme',
}

export enum EvacuationStatus {
  NO_ORDER = 'no_order',
  VOLUNTARY = 'voluntary',
  MANDATORY = 'mandatory',
}

export enum ShelterServiceType {
  ADA_ACCESSIBLE = 'ada_accessible',
  PETS_ALLOWED = 'pets_allowed',
  MEDICAL_CLINIC = 'medical_clinic',
  MENTAL_HEALTH = 'mental_health',
  FOOD_SERVICE = 'food_service',
  CHARGING_STATIONS = 'charging_stations',
  TRANSPORTATION = 'transportation',
}

export enum AQICategory {
  GOOD = 'good',
  MODERATE = 'moderate',
  UNHEALTHY_SENSITIVE = 'unhealthy_sensitive',
  UNHEALTHY = 'unhealthy',
  VERY_UNHEALTHY = 'very_unhealthy',
  HAZARDOUS = 'hazardous',
}
```

---

### Interfaces

```typescript
export interface EmergencyAlert {
  alert_id: string;
  type: AlertType;
  severity: Severity;
  area: string;
  title: string;
  message: string;
  issued_at: string; // ISO datetime
  expires_at: string | null; // ISO datetime
  source: string;
  affected_zip_codes: string[];
  last_updated: string; // ISO datetime
}

export interface EvacuationOrder {
  order_id: string;
  zone: string;
  status: EvacuationStatus;
  issued_at: string; // ISO datetime
  expires_at: string | null; // ISO datetime
  affected_zip_codes: string[];
  affected_addresses: string[];
  recommended_routes: string[];
  road_closures: string[];
  shelter_ids: string[];
  instructions: string;
  source: string;
  last_updated: string; // ISO datetime
}

export interface Shelter {
  shelter_id: string;
  name: string;
  address: string;
  city: string;
  zip_code: string;
  latitude: number | null;
  longitude: number | null;
  capacity_current: number;
  capacity_max: number;
  is_at_capacity: boolean;
  services: ShelterServiceType[];
  hours: string;
  contact_phone: string;
  contact_email: string | null;
  notes: string;
  capacity_last_updated: string; // ISO datetime
  is_open: boolean;
  last_updated: string; // ISO datetime
  distance_miles?: number; // Calculated client-side for sorting
}

export interface AirQualityReport {
  location: string;
  latitude: number | null;
  longitude: number | null;
  aqi: number; // 0-500
  category: AQICategory;
  pm25: number | null;
  pm10: number | null;
  ozone: number | null;
  health_guidance: string;
  forecast: string | null;
  monitoring_station: string;
  updated_at: string; // ISO datetime
  source: string;
}

export interface Location {
  address: string | null;
  zip_code: string;
  city: string | null;
  county: string | null;
  latitude: number | null;
  longitude: number | null;
  alert_zones: string[];
}

export interface TranslationResponse {
  original_text: string;
  translated_text: string;
  source_language: string;
  target_language: string;
  cached: boolean; // True if returned from cache
}
```

---

## Mock Data Samples

### Mock Emergency Alert (backend/mocks/emergency_alerts.json)

```json
[
  {
    "alert_id": "fire_la_20260402_001",
    "type": "fire",
    "severity": "urgent",
    "area": "Los Angeles County - Topanga Canyon area",
    "title": "Wildfire Warning - Topanga Canyon Fire",
    "message": "A fast-moving wildfire has been reported in Topanga Canyon. Residents in the area should prepare for possible evacuation. Monitor local news and emergency alerts.",
    "issued_at": "2026-04-02T14:30:00Z",
    "expires_at": null,
    "source": "LA County Fire Department",
    "affected_zip_codes": ["90290", "90265", "90272"],
    "last_updated": "2026-04-02T15:45:00Z"
  },
  {
    "alert_id": "aqi_sf_20260402_002",
    "type": "air_quality",
    "severity": "warning",
    "area": "San Francisco Bay Area",
    "title": "Unhealthy Air Quality - Wildfire Smoke",
    "message": "Air quality is unhealthy due to smoke from regional wildfires. Limit outdoor activity. Use N95 masks if you must go outside.",
    "issued_at": "2026-04-02T08:00:00Z",
    "expires_at": "2026-04-03T20:00:00Z",
    "source": "Bay Area AQMD",
    "affected_zip_codes": ["94102", "94103", "94105", "94110", "94111"],
    "last_updated": "2026-04-02T16:00:00Z"
  }
]
```

### Mock Shelter (backend/mocks/shelters.json)

```json
[
  {
    "shelter_id": "shelter_la_redcross_001",
    "name": "Red Cross Emergency Shelter - Santa Monica HS",
    "address": "601 Pico Blvd, Santa Monica, CA",
    "city": "Santa Monica",
    "zip_code": "90405",
    "latitude": 34.0151,
    "longitude": -118.4916,
    "capacity_current": 85,
    "capacity_max": 150,
    "is_at_capacity": false,
    "services": ["ada_accessible", "pets_allowed", "food_service", "charging_stations"],
    "hours": "24/7",
    "contact_phone": "310-555-0199",
    "contact_email": "shelter-sm@redcross.org",
    "notes": "Pets must be in crates. Bring vaccination records. Limited medical supplies available.",
    "capacity_last_updated": "2026-04-02T16:30:00Z",
    "is_open": true,
    "last_updated": "2026-04-02T16:30:00Z"
  }
]
```

### Mock Air Quality (backend/mocks/air_quality.json)

```json
[
  {
    "location": "San Francisco - Downtown",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "aqi": 165,
    "category": "unhealthy",
    "pm25": 85.0,
    "pm10": 110.0,
    "ozone": 45.0,
    "health_guidance": "Everyone should reduce prolonged or heavy outdoor exertion. People with respiratory conditions, children, and older adults should avoid outdoor activity.",
    "forecast": "AQI expected to remain Unhealthy (150-200) through tonight. Improvement expected tomorrow morning.",
    "monitoring_station": "San Francisco - 4th Street Station",
    "updated_at": "2026-04-02T16:00:00Z",
    "source": "PurpleAir"
  }
]
```

---

## Notes

- **Translation Caching**: `TranslationCache` stores MD5 hash of source content + target language. Cache key: `{hash}_{target_lang}`. Redis in production (TTL: 24 hours), in-memory dict in dev/test.
- **SMS Session Privacy**: `phone_hash` uses SHA-256 to anonymize phone numbers. Raw phone numbers are never stored.
- **Proper Noun Preservation**: Translation service maintains a list of California location names (cities, counties, streets, shelters) that should NOT be translated. These are excluded from Azure Translator input.
- **Low-Bandwidth Mode**: When `?lowbandwidth=true` or detected via JS, FastAPI serves Jinja2-rendered HTML with inline styles (no external CSS), no JS, and text-only content (<50 KB total).
- **Mock Data Coverage**: Mock JSON includes 20+ alerts (fire, flood, AQI, evacuation), 100+ shelters statewide, 50+ AQI monitoring stations, and 10+ evacuation zones covering major urban areas.
