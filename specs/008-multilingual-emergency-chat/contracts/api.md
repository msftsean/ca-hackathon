# API Contract: Multilingual Emergency Chatbot (008)

**Service**: Multilingual Emergency Chatbot API  
**Base URL**: `http://localhost:8008` (development), `https://emergency.ca.gov` (production)  
**Version**: 1.0.0  
**Date**: 2026-04-02

---

## Endpoints

### Health Check

**`GET /health`**

Health check endpoint for load balancers and monitoring.

**Authentication**: None

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "multilingual-emergency-chat",
  "version": "1.0.0",
  "timestamp": "2026-04-02T10:30:00Z"
}
```

---

### Emergency Alert Lookup

**`POST /emergency/alerts`**

Look up active emergency alerts for a specific location (ZIP code, city, or coordinates).

**Authentication**: None (public endpoint, rate-limited by IP)

**Request Body**:
```json
{
  "location": "94102",
  "language": "es"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `location` | string | Yes | ZIP code, city name, or "lat,lon" coordinates |
| `language` | string | No | Target language code (ISO 639-1: "es", "zh-Hans", "vi", etc.). Defaults to "en". |

**Response** (200 OK):
```json
{
  "location": "94102",
  "alerts": [
    {
      "alert_id": "aqi_sf_20260402_002",
      "type": "air_quality",
      "severity": "warning",
      "area": "San Francisco Bay Area",
      "title": "Calidad del aire no saludable - Humo de incendios forestales",
      "message": "La calidad del aire no es saludable debido al humo de incendios forestales regionales. Limite la actividad al aire libre. Use máscaras N95 si debe salir.",
      "issued_at": "2026-04-02T08:00:00Z",
      "expires_at": "2026-04-03T20:00:00Z",
      "source": "Bay Area AQMD",
      "last_updated": "2026-04-02T16:00:00Z"
    }
  ],
  "language": "es",
  "timestamp": "2026-04-02T16:05:00Z"
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `location` | string | Queried location (echoed from request) |
| `alerts` | array | List of active alerts for this location |
| `alerts[].alert_id` | string | Unique alert identifier |
| `alerts[].type` | string | Alert type ("fire", "flood", "earthquake", "air_quality", "evacuation", "weather", "tsunami", "hazmat", "power_outage") |
| `alerts[].severity` | string | Severity level ("advisory", "warning", "urgent", "extreme") |
| `alerts[].area` | string | Affected area description |
| `alerts[].title` | string | Alert title (translated to target language) |
| `alerts[].message` | string | Detailed alert message (translated) |
| `alerts[].issued_at` | string | ISO 8601 timestamp |
| `alerts[].expires_at` | string | ISO 8601 timestamp (null = until further notice) |
| `alerts[].source` | string | Issuing agency |
| `alerts[].last_updated` | string | ISO 8601 timestamp |
| `language` | string | Language of translated content |
| `timestamp` | string | Response timestamp |

**Status Codes**:
- `200 OK`: Alerts found (may be empty array if no active alerts)
- `400 Bad Request`: Invalid location format
- `429 Too Many Requests`: Rate limit exceeded (30/minute)
- `500 Internal Server Error`: Server error

---

### Evacuation Order Check

**`POST /emergency/evacuation-status`**

Check evacuation order status for a specific location.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "location": "90265",
  "language": "en"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `location` | string | Yes | ZIP code, address, or coordinates |
| `language` | string | No | Target language code (defaults to "en") |

**Response** (200 OK):
```json
{
  "location": "90265",
  "status": "mandatory",
  "zone": "Topanga Canyon - Zone A",
  "issued_at": "2026-04-02T14:30:00Z",
  "expires_at": null,
  "recommended_routes": [
    "Highway 1 South",
    "PCH Northbound"
  ],
  "road_closures": [
    "Topanga Canyon Blvd (north of PCH)",
    "Entrada Dr"
  ],
  "shelter_ids": ["shelter_la_redcross_001", "shelter_la_community_002"],
  "instructions": "Leave immediately. Bring medications, pet supplies, and important documents. Follow designated evacuation routes.",
  "source": "LA County Fire Department",
  "language": "en",
  "last_updated": "2026-04-02T15:45:00Z"
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `location` | string | Queried location |
| `status` | string | Evacuation status ("no_order", "voluntary", "mandatory") |
| `zone` | string | Evacuation zone name |
| `issued_at` | string | ISO 8601 timestamp |
| `expires_at` | string | ISO 8601 timestamp (null = until further notice) |
| `recommended_routes` | array | List of evacuation routes |
| `road_closures` | array | List of closed roads |
| `shelter_ids` | array | IDs of recommended shelters (use with `/emergency/shelters`) |
| `instructions` | string | Evacuation instructions (translated) |
| `source` | string | Issuing authority |
| `language` | string | Language of translated content |
| `last_updated` | string | ISO 8601 timestamp |

**Status Codes**:
- `200 OK`: Evacuation status retrieved (status may be "no_order")
- `400 Bad Request`: Invalid location
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

### Shelter Search

**`POST /emergency/shelters`**

Search for emergency shelters near a location with optional filters (ADA accessible, pets allowed, etc.).

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "location": "90405",
  "max_distance_miles": 10,
  "filters": {
    "ada_accessible": true,
    "pets_allowed": true,
    "has_capacity": true
  },
  "language": "zh-Hans"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `location` | string | Yes | ZIP code, address, or coordinates |
| `max_distance_miles` | number | No | Maximum distance (defaults to 25 miles) |
| `filters` | object | No | Filter criteria |
| `filters.ada_accessible` | boolean | No | Requires ADA accessibility |
| `filters.pets_allowed` | boolean | No | Requires pet acceptance |
| `filters.has_capacity` | boolean | No | Requires available capacity |
| `language` | string | No | Target language code (defaults to "en") |

**Response** (200 OK):
```json
{
  "location": "90405",
  "shelters": [
    {
      "shelter_id": "shelter_la_redcross_001",
      "name": "Red Cross Emergency Shelter - Santa Monica HS",
      "address": "601 Pico Blvd, Santa Monica, CA",
      "city": "Santa Monica",
      "zip_code": "90405",
      "distance_miles": 0.8,
      "capacity_current": 85,
      "capacity_max": 150,
      "is_at_capacity": false,
      "services": ["ada_accessible", "pets_allowed", "food_service", "charging_stations"],
      "hours": "24/7",
      "contact_phone": "310-555-0199",
      "notes": "宠物必须放在笼子里。带上疫苗接种记录。有有限的医疗用品。",
      "capacity_last_updated": "2026-04-02T16:30:00Z",
      "is_open": true
    }
  ],
  "language": "zh-Hans",
  "timestamp": "2026-04-02T16:10:00Z"
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `location` | string | Queried location |
| `shelters` | array | List of shelters (sorted by distance) |
| `shelters[].shelter_id` | string | Unique shelter identifier |
| `shelters[].name` | string | Shelter name (NOT translated — proper noun) |
| `shelters[].address` | string | Street address |
| `shelters[].city` | string | City name |
| `shelters[].zip_code` | string | ZIP code |
| `shelters[].distance_miles` | number | Distance from queried location |
| `shelters[].capacity_current` | number | Current occupancy |
| `shelters[].capacity_max` | number | Maximum capacity |
| `shelters[].is_at_capacity` | boolean | True if full |
| `shelters[].services` | array | Available services (e.g., "ada_accessible", "pets_allowed", "medical_clinic") |
| `shelters[].hours` | string | Operating hours |
| `shelters[].contact_phone` | string | Contact phone number |
| `shelters[].notes` | string | Additional notes (translated) |
| `shelters[].capacity_last_updated` | string | ISO 8601 timestamp |
| `shelters[].is_open` | boolean | True if currently open |
| `language` | string | Language of translated content |
| `timestamp` | string | Response timestamp |

**Status Codes**:
- `200 OK`: Shelters found (may be empty array if none within distance)
- `400 Bad Request`: Invalid location or distance
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

### Air Quality Index (AQI) Lookup

**`POST /emergency/aqi`**

Get current air quality index for a location.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "location": "San Francisco",
  "language": "vi"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `location` | string | Yes | City name, ZIP code, or coordinates |
| `language` | string | No | Target language code (defaults to "en") |

**Response** (200 OK):
```json
{
  "location": "San Francisco - Downtown",
  "aqi": 165,
  "category": "unhealthy",
  "pm25": 85.0,
  "pm10": 110.0,
  "ozone": 45.0,
  "health_guidance": "Mọi người nên giảm hoạt động ngoài trời kéo dài hoặc nặng. Người có bệnh hô hấp, trẻ em và người lớn tuổi nên tránh hoạt động ngoài trời.",
  "forecast": "Dự kiến AQI sẽ duy trì ở mức Không lành mạnh (150-200) suốt đêm nay. Dự kiến cải thiện vào sáng mai.",
  "monitoring_station": "San Francisco - 4th Street Station",
  "updated_at": "2026-04-02T16:00:00Z",
  "source": "PurpleAir",
  "language": "vi"
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `location` | string | Location name |
| `aqi` | number | Air Quality Index (0-500) |
| `category` | string | Health risk category ("good", "moderate", "unhealthy_sensitive", "unhealthy", "very_unhealthy", "hazardous") |
| `pm25` | number | PM2.5 concentration (µg/m³) |
| `pm10` | number | PM10 concentration (µg/m³) |
| `ozone` | number | Ozone concentration (ppb) |
| `health_guidance` | string | Health recommendations (translated) |
| `forecast` | string | 24-hour forecast (translated) |
| `monitoring_station` | string | Data source station name |
| `updated_at` | string | ISO 8601 timestamp |
| `source` | string | Data source (e.g., "PurpleAir", "AirNow") |
| `language` | string | Language of translated content |

**Status Codes**:
- `200 OK`: AQI data retrieved
- `404 Not Found`: No monitoring station near location
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

### Chat Interaction

**`POST /emergency/chat`**

Submit a natural language query to the emergency chatbot. Supports all features (alerts, shelters, AQI, evacuation) via conversational interface.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "session_id": "session_abc123",
  "message": "What's the air quality in San Francisco?",
  "language": "en"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Unique session identifier (UUID) |
| `message` | string | Yes | User's message (1-1000 characters) |
| `language` | string | No | Target language code (auto-detected if not provided) |

**Response** (200 OK):
```json
{
  "session_id": "session_abc123",
  "response": "The air quality in San Francisco is Unhealthy (AQI: 165). Everyone should reduce prolonged outdoor activity. People with respiratory conditions, children, and older adults should avoid outdoor activity.",
  "data": {
    "aqi": 165,
    "category": "unhealthy",
    "location": "San Francisco - Downtown"
  },
  "language": "en",
  "timestamp": "2026-04-02T16:15:00Z"
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Session identifier (echoed from request) |
| `response` | string | Assistant's answer (translated) |
| `data` | object | (Optional) Structured data (alert, shelter, AQI details) |
| `language` | string | Language of response |
| `timestamp` | string | ISO 8601 timestamp |

**Status Codes**:
- `200 OK`: Successful response
- `400 Bad Request`: Invalid request (missing fields, validation errors)
- `429 Too Many Requests`: Rate limit exceeded (30/minute)
- `500 Internal Server Error`: Server error

---

### SMS Inbound Webhook

**`POST /sms/inbound`**

Webhook endpoint for incoming SMS messages. Called by Azure Communication Services when a user texts the emergency chatbot number.

**Authentication**: Yes (Azure Communication Services signature validation)

**Request Body** (Azure Communication Services format):
```json
{
  "from": "+14155551234",
  "to": "+18005551234",
  "message": "What shelters are near 90405?",
  "messageId": "msg_xyz789",
  "timestamp": "2026-04-02T16:20:00Z"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from` | string | Yes | Sender phone number (E.164 format) |
| `to` | string | Yes | Emergency chatbot number |
| `message` | string | Yes | SMS message text |
| `messageId` | string | Yes | Unique message identifier |
| `timestamp` | string | Yes | ISO 8601 timestamp |

**Response** (200 OK):
```json
{
  "status": "processed",
  "sms_sent": true
}
```

**Backend Behavior**:
1. Validate Azure Communication Services signature
2. Hash phone number (SHA-256) for session tracking
3. Process message with `emergency_agent`
4. Send response via Azure Communication Services outbound SMS
5. Return 200 OK to Azure Communication Services

**Status Codes**:
- `200 OK`: Message processed
- `401 Unauthorized`: Invalid signature
- `500 Internal Server Error`: Processing failed

---

### SMS Outbound (Internal)

**`POST /sms/send`** (Internal API — not exposed to public)

Send outbound SMS response. Called by backend after processing inbound SMS.

**Authentication**: Internal only (no external access)

**Request Body**:
```json
{
  "to": "+14155551234",
  "message": "Red Cross Emergency Shelter - Santa Monica HS is 0.8 miles away. 65 beds available. ADA accessible, pets allowed. Call 310-555-0199 for info."
}
```

**Response** (200 OK):
```json
{
  "message_id": "msg_abc456",
  "status": "sent",
  "timestamp": "2026-04-02T16:20:05Z"
}
```

---

### Translation Endpoint

**`POST /translate`**

Translate text between languages. Used internally by frontend for on-the-fly translation of user-submitted queries.

**Authentication**: None (public endpoint, rate-limited)

**Request Body**:
```json
{
  "text": "Where is the nearest shelter?",
  "target_language": "es",
  "source_language": "en"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | Text to translate (1-5000 characters) |
| `target_language` | string | Yes | Target language code (ISO 639-1) |
| `source_language` | string | No | Source language code (auto-detected if not provided) |

**Response** (200 OK):
```json
{
  "original_text": "Where is the nearest shelter?",
  "translated_text": "¿Dónde está el refugio más cercano?",
  "source_language": "en",
  "target_language": "es",
  "cached": false
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `original_text` | string | Original text |
| `translated_text` | string | Translated text |
| `source_language` | string | Detected/provided source language |
| `target_language` | string | Target language |
| `cached` | boolean | True if returned from cache |

**Status Codes**:
- `200 OK`: Translation successful
- `400 Bad Request`: Invalid language code or text too long
- `429 Too Many Requests`: Rate limit exceeded
- `503 Service Unavailable`: Azure Translator unavailable (fallback to English)
- `500 Internal Server Error`: Server error

---

### Low-Bandwidth Mode

**`GET /emergency-low`**

Server-side rendered version of the emergency chatbot for low-bandwidth connections (<200 Kbps). No JavaScript, no React, inline CSS only.

**Authentication**: None

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `location` | string | Pre-fill location (optional) |
| `language` | string | Target language (defaults to "en") |

**Response** (200 OK):
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Emergency Alerts - California</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 10px; }
    .alert { border: 2px solid red; padding: 10px; margin: 10px 0; }
    /* ... inline styles only, <50KB total */
  </style>
</head>
<body>
  <h1>Emergency Alerts</h1>
  <form method="GET" action="/emergency-low">
    <label>Location: <input name="location" value="94102"></label>
    <button type="submit">Get Alerts</button>
  </form>
  <!-- Server-rendered alert content -->
</body>
</html>
```

**Features**:
- No JavaScript required
- Page size <50 KB
- Works on 2G connections
- Accessible via screen readers

---

## Rate Limits

| Endpoint | Limit | Window | Lockout |
|----------|-------|--------|---------|
| `POST /emergency/alerts` | 30 requests | 1 minute | None |
| `POST /emergency/shelters` | 30 requests | 1 minute | None |
| `POST /emergency/aqi` | 30 requests | 1 minute | None |
| `POST /emergency/chat` | 30 requests | 1 minute | None |
| `POST /translate` | 50 requests | 1 minute | None |
| SMS (per phone number) | 10 messages | 1 hour | 1 hour |
| All endpoints combined | 100 requests | 1 minute | 5 minutes |

**Rate Limit Headers** (included in all responses):
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1646230800
```

---

## Error Responses

**Standard Error Format**:
```json
{
  "error": {
    "code": "LOCATION_NOT_FOUND",
    "message": "No alerts found for location '99999'. Please verify the ZIP code.",
    "details": {
      "location": "99999"
    }
  },
  "timestamp": "2026-04-02T16:25:00Z"
}
```

**Common Error Codes**:
- `INVALID_REQUEST`: Validation error (missing required fields)
- `LOCATION_NOT_FOUND`: Location not found in database
- `TRANSLATION_UNAVAILABLE`: Azure Translator unavailable (fallback to English)
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVICE_UNAVAILABLE`: Azure OpenAI or Azure AI Search unavailable

---

## Example Workflows

### Workflow 1: Alert Lookup (Web)
1. User enters ZIP code "94102" and selects language "Spanish"
2. Frontend calls `POST /emergency/alerts` with `{"location": "94102", "language": "es"}`
3. Backend translates alert to Spanish, returns response
4. Frontend displays alert card with translated content

### Workflow 2: Shelter Search (SMS)
1. User texts "Shelters near 90405" to emergency chatbot number
2. Azure Communication Services calls `POST /sms/inbound` webhook
3. Backend processes query, calls `shelter_service.search_shelters("90405")`
4. Backend sends SMS response: "Red Cross Emergency Shelter - Santa Monica HS is 0.8 miles away..."

### Workflow 3: AQI Check (Chat)
1. User sends "What's the air quality in San Francisco?" via chat interface
2. Frontend calls `POST /emergency/chat` with message
3. Backend detects AQI query, calls `aqi_service.get_aqi("San Francisco")`
4. Backend translates response, returns to frontend

### Workflow 4: Low-Bandwidth Mode
1. User on 2G connection visits emergency.ca.gov
2. Frontend detects slow network (<200 Kbps)
3. Frontend redirects to `/emergency-low?location=94102`
4. Backend serves server-rendered HTML with inline styles
5. User submits form, gets new page with alerts (no JS)
