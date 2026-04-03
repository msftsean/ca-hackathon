# API Contracts: Wildfire Response Coordinator

**Feature**: Wildfire Response Coordinator  
**Version**: 1.0  
**Date**: 2026-02-02  
**Base URL**: `http://localhost:8002` (development), `https://wildfire-coordinator.calfire.ca.gov` (production)

## Overview

This document defines all HTTP endpoints for the Wildfire Response Coordinator backend API. All endpoints return JSON unless otherwise specified. Authentication is required for all endpoints via Azure Entra ID (CAL FIRE, Cal OES, county coordinators).

---

## Health and Status Endpoints

### GET /health

Health check endpoint for monitoring and load balancer probes.

**Authentication**: None

**Request**: None

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "wildfire-response-coordinator",
  "version": "1.0.0",
  "timestamp": "2026-02-02T14:30:00Z",
  "dependencies": {
    "azure_openai": "healthy",
    "azure_maps": "healthy",
    "postgres": "healthy",
    "redis": "healthy",
    "weather_api": "healthy",
    "caltrans_511": "healthy"
  }
}
```

**Mock Mode Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "wildfire-response-coordinator",
  "version": "1.0.0",
  "timestamp": "2026-02-02T14:30:00Z",
  "dependencies": {
    "azure_openai": "mock",
    "azure_maps": "mock",
    "postgres": "healthy",
    "redis": "mock",
    "weather_api": "mock",
    "caltrans_511": "mock"
  },
  "mock_mode": true
}
```

**Error Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "service": "wildfire-response-coordinator",
  "errors": [
    "Azure OpenAI connection failed",
    "Weather API timeout"
  ]
}
```

---

## Incident Management Endpoints

### POST /incidents

Create a new wildfire or emergency incident.

**Authentication**: Required (CAL FIRE, Cal OES, county coordinators)

**Request Headers**:
- `Content-Type: application/json`
- `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "incident_type": "wildfire",
  "incident_name": "Paradise Fire",
  "location": {
    "lat": 39.7596,
    "lon": -121.6219
  },
  "location_description": "5 miles NE of Paradise, Butte County",
  "size_acres": 50,
  "discovered_at": "2026-02-02T13:00:00Z",
  "severity": "initial_attack"
}
```

**Request Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `incident_type` | String (enum) | Yes | `wildfire`, `earthquake`, `flood`, `hazmat`, `multi_hazard` |
| `incident_name` | String | No | Common name for incident (auto-generated if not provided) |
| `location` | Object {lat, lon} | Yes | Incident origin coordinates |
| `location_description` | String | Yes | Human-readable location |
| `size_acres` | Decimal | No | Initial fire size (required for wildfires) |
| `discovered_at` | DateTime (ISO 8601) | No | When incident discovered (default: current time) |
| `severity` | String (enum) | No | `initial_attack`, `extended_attack`, `major_emergency`, `catastrophic` (default: auto-determined) |

**Response** (201 Created):
```json
{
  "incident_id": "bb0e8400-e29b-41d4-a716-446655440555",
  "incident_number": "CA-BTU-024561",
  "incident_type": "wildfire",
  "incident_name": "Paradise Fire",
  "location": {
    "lat": 39.7596,
    "lon": -121.6219
  },
  "location_description": "5 miles NE of Paradise, Butte County",
  "county": "Butte",
  "counties_affected": ["Butte"],
  "mutual_aid_regions": [1],
  "lead_agency": "CAL FIRE",
  "supporting_agencies": ["Butte County Fire"],
  "severity": "initial_attack",
  "status": "active",
  "size_acres": 50,
  "created_at": "2026-02-02T14:30:00Z",
  "timeline": [
    {
      "event_id": "cc0e8400-e29b-41d4-a716-446655440666",
      "timestamp": "2026-02-02T14:30:00Z",
      "event_type": "incident_start",
      "description": "Incident created: Paradise Fire (wildfire, 50 acres, Butte County)",
      "actor": "coordinator@calfire.ca.gov",
      "high_risk_decision": false
    }
  ]
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `incident_id` | UUID | Unique identifier for incident |
| `incident_number` | String | Human-readable incident number (format: CA-{county_code}-{sequence}) |
| `lead_agency` | String | Auto-assigned lead agency based on incident type |
| `mutual_aid_regions` | Array of integers | Affected Cal OES mutual aid regions (I-VI: 1-6) |
| `timeline` | Array | Initial timeline event (incident creation) |

**Error Response** (400 Bad Request):
```json
{
  "error": "validation_error",
  "message": "size_acres required for wildfire incidents",
  "details": {
    "field": "size_acres",
    "constraint": "required when incident_type=wildfire"
  }
}
```

---

### GET /incidents

List all active incidents with optional filters.

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | String (enum) | Filter by status: `active`, `contained`, `controlled`, `out` |
| `incident_type` | String (enum) | Filter by type: `wildfire`, `earthquake`, `flood`, `hazmat` |
| `county` | String | Filter by county |
| `mutual_aid_region` | Integer (1-6) | Filter by mutual aid region |
| `limit` | Integer | Max results (default: 50, max: 200) |
| `offset` | Integer | Pagination offset (default: 0) |

**Response** (200 OK):
```json
{
  "incidents": [
    {
      "incident_id": "bb0e8400-e29b-41d4-a716-446655440555",
      "incident_number": "CA-BTU-024561",
      "incident_name": "Paradise Fire",
      "incident_type": "wildfire",
      "location": {"lat": 39.7596, "lon": -121.6219},
      "county": "Butte",
      "lead_agency": "CAL FIRE",
      "severity": "initial_attack",
      "status": "active",
      "size_acres": 50,
      "created_at": "2026-02-02T14:30:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

### GET /incidents/{incident_id}

Retrieve detailed information about a specific incident.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `incident_id` | UUID | Incident identifier |

**Response** (200 OK):
```json
{
  "incident_id": "bb0e8400-e29b-41d4-a716-446655440555",
  "incident_number": "CA-BTU-024561",
  "incident_type": "wildfire",
  "incident_name": "Paradise Fire",
  "location": {"lat": 39.7596, "lon": -121.6219},
  "location_description": "5 miles NE of Paradise, Butte County",
  "county": "Butte",
  "counties_affected": ["Butte"],
  "mutual_aid_regions": [1],
  "lead_agency": "CAL FIRE",
  "supporting_agencies": ["Butte County Fire", "USFS"],
  "severity": "extended_attack",
  "status": "active",
  "created_at": "2026-02-02T14:30:00Z",
  "discovered_at": "2026-02-02T13:00:00Z",
  "size_acres": 250,
  "perimeter": {
    "type": "Polygon",
    "coordinates": [[[...]]],
    "last_updated": "2026-02-02T15:00:00Z"
  },
  "structures_threatened": 150,
  "structures_damaged": 5,
  "structures_destroyed": 2,
  "evacuations_ordered": true,
  "red_flag_warning_active": true,
  "incident_commander": "Chief John Smith",
  "command_post_location": "Paradise Elementary School parking lot",
  "timeline": [...],
  "resources_assigned": 15,
  "evacuation_zones": 3
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "incident_not_found",
  "message": "Incident bb0e8400-e29b-41d4-a716-446655440555 not found"
}
```

---

### PATCH /incidents/{incident_id}

Update incident details (size, status, perimeter, etc.).

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `incident_id` | UUID | Incident identifier |

**Request Body**:
```json
{
  "size_acres": 250,
  "status": "active",
  "severity": "extended_attack",
  "perimeter": {
    "type": "Polygon",
    "coordinates": [[[-121.62, 39.76], [-121.60, 39.76], [-121.60, 39.74], [-121.62, 39.74], [-121.62, 39.76]]]
  },
  "structures_threatened": 150,
  "evacuations_ordered": true
}
```

**Response** (200 OK):
```json
{
  "incident_id": "bb0e8400-e29b-41d4-a716-446655440555",
  "size_acres": 250,
  "status": "active",
  "severity": "extended_attack",
  "updated_at": "2026-02-02T15:00:00Z",
  "timeline_event_added": {
    "event_id": "dd0e8400-e29b-41d4-a716-446655440777",
    "event_type": "size_update",
    "description": "Incident size updated to 250 acres",
    "timestamp": "2026-02-02T15:00:00Z"
  }
}
```

---

## Resource Management Endpoints

### GET /resources

List all resources with optional filters.

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | String (enum) | Filter by status: `available`, `deployed`, `en_route`, `out_of_service` |
| `resource_type` | String (enum) | Filter by type: `engine`, `hand_crew`, `dozer`, `water_tender`, `helicopter`, `air_tanker` |
| `mutual_aid_region` | Integer (1-6) | Filter by home region |
| `agency` | String | Filter by agency (e.g., "CAL FIRE", "USFS") |
| `limit` | Integer | Max results (default: 100, max: 500) |

**Response** (200 OK):
```json
{
  "resources": [
    {
      "resource_id": "ee0e8400-e29b-41d4-a716-446655440888",
      "resource_identifier": "E-57",
      "resource_type": "engine",
      "unit_name": "Sacramento Metropolitan Fire",
      "agency": "CAL FIRE",
      "mutual_aid_region": 3,
      "status": "available",
      "home_station": "Station 57, Sacramento",
      "capability_rating": 1,
      "crew_size": 3
    }
  ],
  "total": 1,
  "limit": 100
}
```

---

### POST /incidents/{incident_id}/resources

Request resource allocation recommendations for an incident.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `incident_id` | UUID | Incident identifier |

**Request Body** (optional):
```json
{
  "fire_behavior": {
    "wind_speed_mph": 25,
    "wind_direction_degrees": 270,
    "terrain": "steep",
    "red_flag_warning": true
  },
  "priorities": ["life_safety", "structure_protection", "fire_containment"]
}
```

**Response** (200 OK):
```json
{
  "incident_id": "bb0e8400-e29b-41d4-a716-446655440555",
  "recommendations": [
    {
      "resource_id": "ee0e8400-e29b-41d4-a716-446655440888",
      "resource_identifier": "E-57",
      "resource_type": "engine",
      "unit_name": "Sacramento Metropolitan Fire",
      "rationale": "Type 1 engine available 45 miles from incident, suitable for structure protection",
      "priority": "high",
      "estimated_arrival": "2026-02-02T15:30:00Z",
      "confidence": 0.92
    },
    {
      "resource_id": "ff0e8400-e29b-41d4-a716-446655440999",
      "resource_identifier": "HEL-301",
      "resource_type": "helicopter",
      "unit_name": "CAL FIRE Helitack",
      "rationale": "Helicopter recommended for air attack in steep terrain, winds acceptable (<30 mph)",
      "priority": "high",
      "estimated_arrival": "2026-02-02T15:15:00Z",
      "confidence": 0.88
    }
  ],
  "mutual_aid_required": false,
  "reserved_for_new_starts": 5,
  "total_available_in_region": 12,
  "high_risk_decision": true,
  "processing_time_ms": 3200
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `recommendations` | Array | Prioritized resource deployment recommendations |
| `rationale` | String | AI-generated reasoning for each recommendation |
| `mutual_aid_required` | Boolean | Whether mutual aid from adjacent regions needed |
| `high_risk_decision` | Boolean | Flagged per EO N-12-23 if resource shortage detected |

---

### POST /incidents/{incident_id}/resources/assign

Assign a resource to an incident.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `incident_id` | UUID | Incident identifier |

**Request Body**:
```json
{
  "resource_id": "ee0e8400-e29b-41d4-a716-446655440888",
  "deployment_time": "2026-02-02T15:00:00Z",
  "estimated_arrival": "2026-02-02T15:45:00Z"
}
```

**Response** (201 Created):
```json
{
  "assignment_id": "gg0e8400-e29b-41d4-a716-446655441000",
  "resource_id": "ee0e8400-e29b-41d4-a716-446655440888",
  "incident_id": "bb0e8400-e29b-41d4-a716-446655440555",
  "resource_identifier": "E-57",
  "status": "en_route",
  "deployment_time": "2026-02-02T15:00:00Z",
  "estimated_arrival": "2026-02-02T15:45:00Z",
  "timeline_event_added": {
    "event_type": "resource_deployment",
    "description": "E-57 (Sacramento Metropolitan Fire) assigned to Paradise Fire"
  }
}
```

---

## Evacuation Planning Endpoints

### POST /incidents/{incident_id}/evacuations/zones

Generate evacuation zone recommendations.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `incident_id` | UUID | Incident identifier |

**Request Body** (optional):
```json
{
  "fire_perimeter": {
    "type": "Polygon",
    "coordinates": [[...]]
  },
  "wind_direction_degrees": 270,
  "fire_spread_rate_mph": 5,
  "override_zones": []
}
```

**Response** (200 OK):
```json
{
  "incident_id": "bb0e8400-e29b-41d4-a716-446655440555",
  "evacuation_zones": [
    {
      "zone_id": "hh0e8400-e29b-41d4-a716-446655441111",
      "zone_name": "Paradise Zone A",
      "boundaries": {
        "type": "Polygon",
        "coordinates": [[...]]
      },
      "population_estimate": 1500,
      "priority": "immediate",
      "rationale": "Downwind of fire perimeter, predicted spread within 2 hours",
      "evacuation_routes": ["Route 1: Skyway South", "Route 2: Pentz Road"],
      "assembly_points": ["Paradise Fairgrounds", "Chico Walmart Parking Lot"],
      "special_needs": {
        "senior_facilities": 2,
        "medical_facilities": 0,
        "schools": 1
      }
    }
  ],
  "total_population_affected": 1500,
  "high_risk_decision": true,
  "processing_time_ms": 4200
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `zone_id` | UUID | Unique identifier for evacuation zone |
| `priority` | String (enum) | `immediate`, `warning`, `advisory` |
| `rationale` | String | AI-generated reasoning for zone boundaries |
| `high_risk_decision` | Boolean | Always true for evacuation planning (life safety per EO N-12-23) |

---

### POST /incidents/{incident_id}/evacuations/routes

Optimize evacuation routes for a zone.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `incident_id` | UUID | Incident identifier |

**Request Body**:
```json
{
  "zone_id": "hh0e8400-e29b-41d4-a716-446655441111",
  "destinations": [
    {"name": "Paradise Fairgrounds", "lat": 39.7350, "lon": -121.6050}
  ],
  "road_closures": [
    {"road": "Highway 70", "closure_point": {"lat": 39.75, "lon": -121.61}}
  ]
}
```

**Response** (200 OK):
```json
{
  "zone_id": "hh0e8400-e29b-41d4-a716-446655441111",
  "routes": [
    {
      "route_id": "ii0e8400-e29b-41d4-a716-446655441222",
      "route_name": "Route 1: Skyway South",
      "origin": "Paradise Zone A Center",
      "destination": "Paradise Fairgrounds",
      "distance_miles": 3.5,
      "estimated_time_minutes": 15,
      "capacity_vehicles_per_hour": 800,
      "traffic_level": "moderate",
      "waypoints": [
        {"lat": 39.76, "lon": -121.62, "instruction": "Head south on Skyway"},
        {"lat": 39.74, "lon": -121.61, "instruction": "Turn right onto Pentz Road"}
      ],
      "hazards": ["Narrow road section at mile 2.0"],
      "alternative_route": "ii0e8400-e29b-41d4-a716-446655441333"
    }
  ],
  "total_evacuation_time_estimate_hours": 2.5,
  "bottleneck_locations": [
    {"location": "Skyway / Pentz Road intersection", "capacity_reduction": "30%"}
  ],
  "recommendations": [
    "Stagger evacuation by zone to prevent gridlock",
    "Deploy CHP traffic control at Skyway / Pentz Road intersection"
  ],
  "processing_time_ms": 2800
}
```

---

## Weather and Alerts Endpoints

### GET /weather

Get current weather conditions for a location or incident.

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `lat` | Float | Latitude |
| `lon` | Float | Longitude |
| `incident_id` | UUID | Incident identifier (alternative to lat/lon) |

**Response** (200 OK):
```json
{
  "location": {"lat": 39.7596, "lon": -121.6219},
  "timestamp": "2026-02-02T15:00:00Z",
  "temperature_f": 85,
  "humidity_percent": 12,
  "wind_speed_mph": 28,
  "wind_direction_degrees": 270,
  "wind_direction_cardinal": "W",
  "red_flag_warning": {
    "active": true,
    "issued_at": "2026-02-02T06:00:00Z",
    "expires_at": "2026-02-03T18:00:00Z",
    "severity": "extreme",
    "description": "Extremely low humidity and high winds creating critical fire weather conditions"
  },
  "fire_danger_index": "extreme",
  "forecast_24h": {
    "wind_speed_mph_max": 35,
    "humidity_percent_min": 8,
    "temperature_f_max": 92
  },
  "data_source": "National Weather Service",
  "cache_age_seconds": 120
}
```

---

### GET /weather/alerts

List active Red Flag Warnings and fire weather alerts.

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `region` | Integer (1-6) | Mutual aid region |
| `county` | String | California county |

**Response** (200 OK):
```json
{
  "alerts": [
    {
      "alert_id": "jj0e8400-e29b-41d4-a716-446655441444",
      "alert_type": "red_flag_warning",
      "severity": "extreme",
      "issued_at": "2026-02-02T06:00:00Z",
      "expires_at": "2026-02-03T18:00:00Z",
      "affected_regions": [1, 3],
      "affected_counties": ["Butte", "Shasta", "Tehama"],
      "description": "Extremely low humidity and high winds creating critical fire weather conditions",
      "conditions": {
        "wind_speed_mph": "25-35 with gusts to 50",
        "humidity_percent": "5-15",
        "duration_hours": 36
      },
      "recommendations": [
        "Avoid all outdoor burning",
        "Pre-position resources in high-risk areas",
        "Increase staffing for initial attack"
      ]
    }
  ],
  "total": 1
}
```

---

## PSPS Coordination Endpoints

### GET /psps/events

List active and planned PSPS (Public Safety Power Shutoff) events.

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `utility` | String | Filter by utility: `PGE`, `SCE`, `SDGE` |
| `status` | String (enum) | Filter by status: `planned`, `active`, `completed` |
| `county` | String | Filter by county |

**Response** (200 OK):
```json
{
  "events": [
    {
      "psps_id": "kk0e8400-e29b-41d4-a716-446655441555",
      "utility": "PGE",
      "event_name": "North Bay PSPS 2026-02-02",
      "status": "active",
      "de_energization_time": "2026-02-02T22:00:00Z",
      "estimated_restoration_time": "2026-02-04T12:00:00Z",
      "affected_counties": ["Butte", "Tehama", "Glenn"],
      "affected_circuits": 15,
      "customers_affected": 12500,
      "critical_facilities_affected": [
        {"type": "hospital", "name": "Oroville Hospital", "backup_power": true},
        {"type": "water_system", "name": "Paradise Irrigation District", "backup_power": false},
        {"type": "communication", "name": "AT&T Cell Tower BT-451", "backup_power": true}
      ],
      "coordination_status": "resources_deployed",
      "generators_deployed": 3,
      "notes": "Generator support provided for Paradise Irrigation District"
    }
  ],
  "total": 1
}
```

---

### POST /incidents/{incident_id}/psps/coordinate

Request PSPS coordination for an incident.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `incident_id` | UUID | Incident identifier |

**Request Body**:
```json
{
  "utility": "PGE",
  "affected_circuits": ["Circuit 7012", "Circuit 7013"],
  "coordination_type": "power_restoration",
  "notes": "Fire contained in de-energized area, request power restoration timeline"
}
```

**Response** (201 Created):
```json
{
  "coordination_id": "ll0e8400-e29b-41d4-a716-446655441666",
  "incident_id": "bb0e8400-e29b-41d4-a716-446655440555",
  "utility": "PGE",
  "coordination_type": "power_restoration",
  "status": "pending_utility_response",
  "created_at": "2026-02-02T16:00:00Z",
  "expected_response_time": "4 hours",
  "timeline_event_added": {
    "event_type": "psps_coordination",
    "description": "PSPS coordination requested from PG&E for power restoration"
  }
}
```

---

## Timeline and Audit Endpoints

### GET /incidents/{incident_id}/timeline

Retrieve full incident timeline with all events.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `incident_id` | UUID | Incident identifier |

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `event_type` | String (enum) | Filter by event type |
| `high_risk_only` | Boolean | Show only high-risk decisions (EO N-12-23) |
| `limit` | Integer | Max results (default: 100) |

**Response** (200 OK):
```json
{
  "incident_id": "bb0e8400-e29b-41d4-a716-446655440555",
  "timeline": [
    {
      "event_id": "cc0e8400-e29b-41d4-a716-446655440666",
      "timestamp": "2026-02-02T14:30:00Z",
      "event_type": "incident_start",
      "description": "Incident created: Paradise Fire (wildfire, 50 acres, Butte County)",
      "actor": "coordinator@calfire.ca.gov",
      "reasoning": null,
      "data_snapshot": {
        "size_acres": 50,
        "severity": "initial_attack"
      },
      "high_risk_decision": false
    },
    {
      "event_id": "dd0e8400-e29b-41d4-a716-446655440777",
      "timestamp": "2026-02-02T15:00:00Z",
      "event_type": "evacuation_order",
      "description": "Evacuation order issued for Paradise Zone A (1500 residents)",
      "actor": "incident_commander@calfire.ca.gov",
      "reasoning": "Fire spreading rapidly downwind due to 28 mph west winds and 12% humidity. Predicted arrival at Paradise Zone A within 2 hours. Life safety priority.",
      "data_snapshot": {
        "wind_speed_mph": 28,
        "fire_spread_rate_mph": 5,
        "population_affected": 1500
      },
      "high_risk_decision": true
    }
  ],
  "total": 2
}
```

---

## WebSocket Real-Time Updates

### WebSocket /ws/incidents

Real-time incident updates via WebSocket.

**Authentication**: Required (token in query param: `/ws/incidents?token=<bearer_token>`)

**Connection**:
```javascript
const ws = new WebSocket('wss://wildfire-coordinator.calfire.ca.gov/ws/incidents?token=<token>');
```

**Message Format (server → client)**:
```json
{
  "type": "incident_update",
  "incident_id": "bb0e8400-e29b-41d4-a716-446655440555",
  "timestamp": "2026-02-02T15:30:00Z",
  "changes": {
    "size_acres": 350,
    "severity": "extended_attack"
  },
  "timeline_event": {
    "event_type": "size_update",
    "description": "Incident size updated to 350 acres"
  }
}
```

**Message Types**:
- `incident_update`: Incident field changes
- `resource_deployed`: Resource assigned to incident
- `evacuation_order`: New evacuation zone created
- `weather_alert`: Red Flag Warning or critical weather change
- `psps_event`: PSPS event created or updated

---

## Status Codes Summary

| Status Code | Meaning | Used For |
|-------------|---------|----------|
| **200 OK** | Success | GET requests returning data |
| **201 Created** | Resource created | POST /incidents, POST /resources/assign, POST /psps/coordinate |
| **400 Bad Request** | Invalid request | Validation errors, missing required fields |
| **401 Unauthorized** | Authentication failed | Missing or invalid Bearer token |
| **403 Forbidden** | Access denied | User lacks permission for this incident/region |
| **404 Not Found** | Resource not found | Incident, resource, or zone does not exist |
| **503 Service Unavailable** | Service degraded | Azure OpenAI outage, weather API timeout |

---

## Authentication

All endpoints except `/health` require Azure Entra ID authentication.

**Authentication Method**: Azure Entra ID (OAuth 2.0)
- Header: `Authorization: Bearer <token>`
- Token obtained via Azure Entra ID authentication flow
- Scope: `api://wildfire-coordinator/.default`

**Role-Based Access**:
- **CAL FIRE Coordinators**: Full access to all incidents and resources
- **Cal OES Coordinators**: Full access to all incidents and resources
- **County Coordinators**: Access limited to incidents in their county and assigned mutual aid region
- **Utility Coordinators**: Read-only access, PSPS coordination endpoints only

---

## Rate Limiting

- **Authenticated endpoints**: 100 requests/minute per user
- **WebSocket connections**: 1 connection per user (reconnect if disconnected)
- Rate limit headers included in all responses:
  - `X-RateLimit-Limit: 100`
  - `X-RateLimit-Remaining: 85`
  - `X-RateLimit-Reset: 1643817600`

---

## CORS Configuration

- **Development**: `http://localhost:3000` (frontend dev server)
- **Production**: `https://wildfire-coordinator.calfire.ca.gov`, `https://caloesportal.ca.gov`
- **Methods**: GET, POST, PATCH, OPTIONS
- **Headers**: Content-Type, Authorization

---

**Last Updated**: 2026-02-02  
**Next Review**: After pilot deployment (Q3 2026, pre-fire-season)
