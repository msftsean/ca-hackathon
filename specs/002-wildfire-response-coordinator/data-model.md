# Data Model: Wildfire Response Coordinator

**Feature**: Wildfire Response Coordinator  
**Version**: 1.0  
**Date**: 2026-02-02

## Overview

This document defines the core entities and relationships for the Wildfire Response Coordinator. The data model supports incident assessment, lead agency mapping, resource allocation across 6 Cal OES mutual aid regions, evacuation planning, weather integration, and utility PSPS coordination while maintaining Constitutional compliance and Executive Order N-12-23 high-risk use case reporting.

---

## Core Entities

### 1. Incident

Represents a wildfire or emergency event requiring multi-agency coordination.

**Attributes**:
- `incident_id` (UUID, primary key): Unique identifier for the incident
- `incident_number` (string, unique): Human-readable incident number (e.g., "CA-BTU-024561")
- `incident_type` (enum): "wildfire", "earthquake", "flood", "hazmat", "multi_hazard"
- `incident_name` (string): Common name for the incident (e.g., "Dixie Fire", "Camp Fire")
- `location` (geography point): Incident origin coordinates (latitude/longitude)
- `location_description` (string): Human-readable location (e.g., "5 miles NE of Paradise, Butte County")
- `county` (string): Primary California county affected
- `counties_affected` (array of strings): All California counties affected
- `mutual_aid_regions` (array of integers): Affected Cal OES mutual aid regions (I-VI)
- `lead_agency` (string): Lead agency determined by incident type ("CAL FIRE", "Cal OES", "DWR", "CHP")
- `supporting_agencies` (array of strings): Supporting agencies involved (e.g., "County Fire", "CHP", "PG&E")
- `severity` (enum): "initial_attack", "extended_attack", "major_emergency", "catastrophic"
- `status` (enum): "active", "contained", "controlled", "out", "under_investigation"
- `created_at` (datetime): When the incident was created in the system
- `discovered_at` (datetime): When the incident was first discovered
- `contained_at` (datetime, nullable): When the incident was contained
- `controlled_at` (datetime, nullable): When the incident was controlled
- `size_acres` (decimal, nullable): Fire size in acres (for wildfires)
- `perimeter` (geography polygon, nullable): Current fire perimeter
- `structures_threatened` (integer, nullable): Number of structures threatened
- `structures_damaged` (integer, nullable): Number of structures damaged
- `structures_destroyed` (integer, nullable): Number of structures destroyed
- `evacuations_ordered` (boolean): Whether evacuation orders have been issued
- `red_flag_warning_active` (boolean): Whether a Red Flag Warning is active in the area
- `incident_commander` (string, nullable): Name of incident commander
- `command_post_location` (string, nullable): Location of incident command post

**Relationships**:
- One-to-many with `IncidentTimeline` (incident events over time)
- One-to-many with `ResourceAssignment` (resources assigned to this incident)
- One-to-many with `EvacuationZone` (evacuation zones for this incident)
- One-to-many with `AgencyAssignment` (agencies assigned to this incident)
- One-to-many with `WeatherObservation` (weather conditions at incident)

**Indexes**:
- Primary key on `incident_id`
- Unique index on `incident_number`
- Index on `status` for active incident queries
- Geospatial index on `location` for proximity queries
- Geospatial index on `perimeter` for spatial analysis
- Index on `created_at` for temporal queries
- Index on `lead_agency` for agency-specific reporting

**Constitutional Compliance**:
- All incident decisions logged per Auditability (Principle V)
- Incident data considered public information per California Emergency Services Act
- High-risk decisions (evacuations) flagged per EO N-12-23

---

### 2. IncidentTimeline

Represents key events in an incident's lifecycle.

**Attributes**:
- `event_id` (UUID, primary key): Unique identifier for the timeline event
- `incident_id` (UUID, foreign key): Reference to parent Incident
- `timestamp` (datetime): When the event occurred
- `event_type` (enum): "incident_start", "agency_assignment", "resource_deployment", "evacuation_order", "size_update", "containment_increase", "weather_change", "psps_coordination", "incident_contained", "incident_controlled", "incident_out"
- `description` (text): Human-readable event description
- `actor` (string, nullable): Who made the decision (incident commander, coordinator name)
- `reasoning` (text, nullable): Why this decision was made (for audit and after-action review)
- `data_snapshot` (JSON): Snapshot of relevant data at time of event (size, resources, weather)
- `high_risk_decision` (boolean): Whether this event involved a high-risk decision per EO N-12-23

**Relationships**:
- Many-to-one with `Incident`

**Indexes**:
- Primary key on `event_id`
- Foreign key index on `incident_id`
- Index on `timestamp` for temporal queries
- Index on `event_type` for event-specific queries
- Index on `high_risk_decision` for EO N-12-23 reporting

**Constitutional Compliance**:
- All timeline events logged for Auditability (Principle V)
- High-risk decisions flagged per EO N-12-23
- Reasoning preserved for after-action reviews and public accountability

---

### 3. Resource

Represents a firefighting or emergency resource (engine, crew, aircraft, dozer, command vehicle).

**Attributes**:
- `resource_id` (UUID, primary key): Unique identifier for the resource
- `resource_identifier` (string, unique): Unit identifier (e.g., "E-57", "HEL-301", "T-47 DOZ")
- `resource_type` (enum): "engine", "hand_crew", "dozer", "water_tender", "helicopter", "air_tanker", "overhead", "support"
- `unit_name` (string): Name of the unit (e.g., "Sacramento Metropolitan Fire", "Hotshot Crew 7")
- `home_station` (string): Home station location
- `home_location` (geography point): Home station coordinates
- `mutual_aid_region` (integer): Home Cal OES mutual aid region (I-VI: 1-6)
- `agency` (string): Parent agency (e.g., "CAL FIRE", "USFS", "County Fire")
- `status` (enum): "available", "deployed", "en_route", "out_of_service", "on_order"
- `current_location` (geography point, nullable): Current location if deployed
- `assigned_incident_id` (UUID, foreign key, nullable): Reference to Incident if deployed
- `deployment_time` (datetime, nullable): When resource was deployed to current incident
- `estimated_arrival` (datetime, nullable): ETA if en_route
- `capability_rating` (integer, 1-5): Resource capability level (1=Type 1, most capable)
- `crew_size` (integer, nullable): Number of personnel on this resource
- `maintenance_due` (date, nullable): Next scheduled maintenance date

**Relationships**:
- Many-to-one with `Incident` (via assigned_incident_id, if deployed)
- One-to-many with `ResourceAssignment` (assignment history)

**Indexes**:
- Primary key on `resource_id`
- Unique index on `resource_identifier`
- Index on `status` for available resource queries
- Index on `mutual_aid_region` for regional resource queries
- Geospatial index on `home_location` for proximity queries
- Geospatial index on `current_location` for deployed resource tracking
- Foreign key index on `assigned_incident_id`

**Constitutional Compliance**:
- Resource allocation tracked per Auditability (Principle V)
- Equity in resource distribution across counties per Equity (Principle III)

---

### 4. ResourceAssignment

Represents the assignment of a resource to an incident (historical record).

**Attributes**:
- `assignment_id` (UUID, primary key): Unique identifier for the assignment
- `resource_id` (UUID, foreign key): Reference to Resource
- `incident_id` (UUID, foreign key): Reference to Incident
- `assigned_at` (datetime): When resource was assigned
- `deployed_at` (datetime, nullable): When resource arrived on scene
- `demobilized_at` (datetime, nullable): When resource was released from incident
- `assignment_reason` (text): Why this resource was selected (for audit and learning)
- `recommendation_confidence` (float, 0.0-1.0): AI confidence in this assignment recommendation
- `approved_by` (string, nullable): Incident commander who approved the assignment

**Relationships**:
- Many-to-one with `Resource`
- Many-to-one with `Incident`

**Indexes**:
- Primary key on `assignment_id`
- Foreign key indexes on `resource_id` and `incident_id`
- Index on `assigned_at` for temporal queries

**Constitutional Compliance**:
- Assignment reasoning logged per Auditability (Principle V)
- Supports after-action review and resource allocation optimization

---

### 5. EvacuationZone

Represents a geographic area requiring evacuation due to an incident.

**Attributes**:
- `zone_id` (UUID, primary key): Unique identifier for the evacuation zone
- `incident_id` (UUID, foreign key): Reference to parent Incident
- `zone_name` (string): Human-readable zone name (e.g., "Zone A", "Paradise North")
- `boundaries` (geography polygon): Geographic boundaries of the zone
- `population_estimate` (integer): Estimated population in the zone
- `households_estimate` (integer): Estimated number of households
- `vulnerable_populations` (JSON): Special considerations (elderly care facilities, schools, hospitals)
- `status` (enum): "pre_evacuation_warning", "evacuation_order", "evacuation_complete", "repopulation_allowed", "repopulation_complete"
- `ordered_at` (datetime, nullable): When evacuation order was issued
- `reason` (text): Why evacuation was ordered (fire proximity, wind shift, etc.)
- `evacuation_routes` (array of UUIDs): References to EvacuationRoute for this zone
- `assembly_points` (JSON array): Designated assembly/shelter locations
- `estimated_evacuation_time` (integer, nullable): Estimated minutes to evacuate zone
- `actual_evacuation_time` (integer, nullable): Actual minutes taken to evacuate
- `priority` (integer): Evacuation priority (1=highest, based on threat level)

**Relationships**:
- Many-to-one with `Incident`
- One-to-many with `EvacuationRoute` (via evacuation_routes array)

**Indexes**:
- Primary key on `zone_id`
- Foreign key index on `incident_id`
- Geospatial index on `boundaries` for spatial analysis
- Index on `status` for active evacuation tracking
- Index on `priority` for triage

**Constitutional Compliance**:
- Evacuation decisions logged as high-risk per EO N-12-23
- Vulnerable populations flagged per Equity (Principle III)
- Multi-language notifications required per Accessibility (Principle II)

---

### 6. EvacuationRoute

Represents an optimized evacuation route from a zone to safety.

**Attributes**:
- `route_id` (UUID, primary key): Unique identifier for the route
- `zone_id` (UUID, foreign key): Reference to EvacuationZone
- `route_name` (string): Human-readable route name (e.g., "Skyway South Route")
- `route_geometry` (geography linestring): Geographic path of the route
- `start_point` (geography point): Route origin
- `end_point` (geography point): Route destination (assembly point)
- `distance_miles` (decimal): Route distance in miles
- `estimated_travel_time_minutes` (integer): Estimated travel time without traffic
- `traffic_capacity_vehicles_per_hour` (integer): Estimated traffic capacity
- `road_closures` (JSON array): Known road closures or hazards on this route
- `status` (enum): "open", "congested", "closed"
- `priority` (integer): Route priority (1=primary, 2=alternate, etc.)
- `last_updated` (datetime): When route status was last updated

**Relationships**:
- Many-to-one with `EvacuationZone`

**Indexes**:
- Primary key on `route_id`
- Foreign key index on `zone_id`
- Geospatial index on `route_geometry`
- Index on `status` for available route queries

**Constitutional Compliance**:
- Route optimization provides equal service to all communities per Equity (Principle III)
- Route status updates support real-time decision-making per Auditability (Principle V)

---

### 7. WeatherCondition

Represents real-time or forecast weather data at an incident location.

**Attributes**:
- `observation_id` (UUID, primary key): Unique identifier for the observation
- `incident_id` (UUID, foreign key, nullable): Reference to Incident if incident-specific
- `location` (geography point): Observation location coordinates
- `location_name` (string, nullable): Human-readable location (e.g., "RAWS Station Paradise")
- `timestamp` (datetime): Observation timestamp
- `observation_type` (enum): "current", "forecast", "red_flag_warning", "fire_weather_watch"
- `wind_speed_mph` (integer): Wind speed in miles per hour
- `wind_direction_degrees` (integer): Wind direction in degrees (0-360, 0=North)
- `wind_gust_mph` (integer, nullable): Wind gust speed
- `temperature_fahrenheit` (integer): Temperature in Fahrenheit
- `relative_humidity_percent` (integer): Relative humidity percentage
- `fuel_moisture_percent` (integer, nullable): Dead fuel moisture percentage (1-hour, 10-hour)
- `red_flag_warning` (boolean): Whether a Red Flag Warning is active
- `fire_weather_watch` (boolean): Whether a Fire Weather Watch is active
- `warning_start` (datetime, nullable): Red Flag Warning start time
- `warning_end` (datetime, nullable): Red Flag Warning end time
- `source` (string): Data source (e.g., "National Weather Service", "RAWS", "NOAA")

**Relationships**:
- Many-to-one with `Incident` (if incident-specific)

**Indexes**:
- Primary key on `observation_id`
- Foreign key index on `incident_id`
- Geospatial index on `location` for proximity queries
- Index on `timestamp` for temporal queries
- Index on `red_flag_warning` for alert queries

**Constitutional Compliance**:
- Weather data sources documented per Auditability (Principle V)
- Red Flag Warnings trigger proactive resource positioning per high-risk use case requirements

---

### 8. AgencyAssignment

Represents an agency's involvement in an incident.

**Attributes**:
- `assignment_id` (UUID, primary key): Unique identifier for the assignment
- `incident_id` (UUID, foreign key): Reference to Incident
- `agency_name` (string): Agency name (e.g., "CAL FIRE", "Cal OES", "Butte County Fire")
- `agency_type` (enum): "lead", "support", "mutual_aid", "federal", "utility"
- `role` (string): Agency role description (e.g., "Incident Command", "Air Operations", "Logistics")
- `contact_name` (string, nullable): Agency representative name
- `contact_phone` (string, nullable): Agency representative phone
- `resources_committed` (integer): Number of resources assigned by this agency
- `assigned_at` (datetime): When agency was assigned
- `demobilized_at` (datetime, nullable): When agency was released from incident

**Relationships**:
- Many-to-one with `Incident`

**Indexes**:
- Primary key on `assignment_id`
- Foreign key index on `incident_id`
- Index on `agency_name` for agency-specific queries
- Index on `agency_type` for lead/support agency queries

**Constitutional Compliance**:
- Multi-agency coordination tracked per Auditability (Principle V)
- Lead agency determination documented per Constitutional requirements

---

### 9. PSPSEvent

Represents a Public Safety Power Shutoff (PSPS) event coordinated with utilities.

**Attributes**:
- `psps_id` (UUID, primary key): Unique identifier for the PSPS event
- `incident_id` (UUID, foreign key, nullable): Reference to Incident if PSPS is incident-driven
- `utility_name` (string): Utility name ("PG&E", "Southern California Edison", "San Diego Gas & Electric")
- `event_name` (string): PSPS event name or identifier
- `affected_counties` (array of strings): California counties affected
- `affected_circuits` (JSON array): Circuit identifiers and locations
- `customer_count` (integer): Number of customers affected
- `critical_facilities_count` (integer): Number of critical facilities affected (hospitals, water systems)
- `de_energization_planned` (datetime): Planned de-energization time
- `de_energization_actual` (datetime, nullable): Actual de-energization time
- `restoration_estimated` (datetime, nullable): Estimated power restoration time
- `restoration_actual` (datetime, nullable): Actual power restoration time
- `status` (enum): "planned", "active", "restoration_in_progress", "restoration_complete", "cancelled"
- `coordination_notes` (text): Coordination notes with utility and incident command
- `resources_deployed` (JSON array): Resources deployed for critical facility support (generators, etc.)

**Relationships**:
- Many-to-one with `Incident` (if incident-driven)

**Indexes**:
- Primary key on `psps_id`
- Foreign key index on `incident_id`
- Index on `utility_name` for utility-specific queries
- Index on `status` for active PSPS tracking
- Index on `de_energization_planned` for temporal queries

**Constitutional Compliance**:
- PSPS coordination decisions logged per Auditability (Principle V)
- Critical facility support prioritized per Equity (Principle III)
- Utility coordination supports Constitutional transparency requirements

---

### 10. MutualAidRegion

Represents one of the 6 Cal OES mutual aid regions in California.

**Attributes**:
- `region_id` (integer, primary key): Region number (1-6, corresponding to I-VI)
- `region_name` (string): Region name ("Northern California", "Bay Area", etc.)
- `boundaries` (geography polygon): Geographic boundaries of the region
- `counties` (array of strings): California counties in this region
- `coordinator_agency` (string): Primary coordinating agency for this region
- `coordinator_contact` (string, nullable): Regional coordinator contact information

**Relationships**:
- One-to-many with `Resource` (resources assigned to this region)

**Indexes**:
- Primary key on `region_id`
- Geospatial index on `boundaries`

**Constitutional Compliance**:
- Regional resource distribution tracked per Equity (Principle III)
- Mutual aid coordination supports Constitutional multi-agency requirements

---

## Entity Relationships Diagram

```
Incident
    ├── incident_id (PK)
    ├── lead_agency
    ├── mutual_aid_regions
    └── status
        │
        ├──> IncidentTimeline
        │       ├── event_id (PK)
        │       ├── incident_id (FK)
        │       ├── event_type
        │       └── high_risk_decision
        │
        ├──> ResourceAssignment
        │       ├── assignment_id (PK)
        │       ├── incident_id (FK)
        │       ├── resource_id (FK) ──> Resource
        │       └── assignment_reason         ├── resource_id (PK)
        │                                      ├── status
        │                                      ├── mutual_aid_region
        │                                      └── home_location
        │
        ├──> EvacuationZone
        │       ├── zone_id (PK)
        │       ├── incident_id (FK)
        │       ├── boundaries
        │       ├── status
        │       └── priority
        │           │
        │           └──> EvacuationRoute
        │                   ├── route_id (PK)
        │                   ├── zone_id (FK)
        │                   ├── route_geometry
        │                   └── status
        │
        ├──> WeatherCondition
        │       ├── observation_id (PK)
        │       ├── incident_id (FK)
        │       ├── location
        │       ├── red_flag_warning
        │       └── wind_speed_mph
        │
        ├──> AgencyAssignment
        │       ├── assignment_id (PK)
        │       ├── incident_id (FK)
        │       ├── agency_name
        │       └── agency_type
        │
        └──> PSPSEvent
                ├── psps_id (PK)
                ├── incident_id (FK)
                ├── utility_name
                ├── status
                └── customer_count

MutualAidRegion
    ├── region_id (PK)
    ├── region_name
    ├── boundaries
    └── counties
```

---

## Data Retention and Privacy

Per California Emergency Services Act and state records retention policies:

- **Incident**: Retained for 10 years per emergency services records retention schedule
- **IncidentTimeline**: Retained for 10 years; supports after-action reviews and public accountability
- **Resource**: Resource inventory retained indefinitely; assignment history for 10 years
- **ResourceAssignment**: Retained for 10 years for after-action review and mutual aid reimbursement
- **EvacuationZone**: Retained for 10 years for after-action review and evacuation planning improvement
- **EvacuationRoute**: Retained for 10 years; route effectiveness analysis for future incidents
- **WeatherCondition**: Retained for 10 years; supports fire behavior research and model improvement
- **AgencyAssignment**: Retained for 10 years per mutual aid records retention requirements
- **PSPSEvent**: Retained for 10 years per utility coordination records retention
- **MutualAidRegion**: Retained indefinitely; updated when regional boundaries change

**Privacy Considerations**:
- Incident data considered public information per California Emergency Services Act
- No constituent PII in wildfire coordination system
- Coordinator names logged for accountability but access controlled to incident command staff
- Critical facility locations (hospitals, water systems) considered sensitive infrastructure data

---

## Sample Data

### Sample Incident

```json
{
  "incident_id": "a10e8400-e29b-41d4-a716-446655440000",
  "incident_number": "CA-BTU-024561",
  "incident_type": "wildfire",
  "incident_name": "Paradise Creek Fire",
  "location": {
    "type": "Point",
    "coordinates": [-121.6219, 39.7596]
  },
  "location_description": "5 miles NE of Paradise, Butte County",
  "county": "Butte",
  "counties_affected": ["Butte", "Plumas"],
  "mutual_aid_regions": [1, 3],
  "lead_agency": "CAL FIRE",
  "supporting_agencies": ["Butte County Fire", "CHP", "Cal OES", "PG&E"],
  "severity": "extended_attack",
  "status": "active",
  "created_at": "2026-07-15T14:00:00Z",
  "discovered_at": "2026-07-15T13:45:00Z",
  "size_acres": 2500.0,
  "structures_threatened": 150,
  "evacuations_ordered": true,
  "red_flag_warning_active": true,
  "incident_commander": "Battalion Chief Sarah Martinez"
}
```

### Sample Resource

```json
{
  "resource_id": "b20e8400-e29b-41d4-a716-446655440111",
  "resource_identifier": "E-57",
  "resource_type": "engine",
  "unit_name": "Sacramento Metropolitan Fire District",
  "home_station": "Station 57 - Rancho Cordova",
  "home_location": {
    "type": "Point",
    "coordinates": [-121.2688, 38.5816]
  },
  "mutual_aid_region": 3,
  "agency": "Sacramento Metro Fire",
  "status": "deployed",
  "assigned_incident_id": "a10e8400-e29b-41d4-a716-446655440000",
  "deployment_time": "2026-07-15T16:30:00Z",
  "capability_rating": 1,
  "crew_size": 4
}
```

### Sample EvacuationZone

```json
{
  "zone_id": "c30e8400-e29b-41d4-a716-446655440222",
  "incident_id": "a10e8400-e29b-41d4-a716-446655440000",
  "zone_name": "Zone A - Paradise North",
  "boundaries": {
    "type": "Polygon",
    "coordinates": [[[-121.62, 39.76], [-121.60, 39.76], [-121.60, 39.78], [-121.62, 39.78], [-121.62, 39.76]]]
  },
  "population_estimate": 3500,
  "households_estimate": 1200,
  "vulnerable_populations": {
    "nursing_homes": 1,
    "schools": 2,
    "assisted_living": 3
  },
  "status": "evacuation_order",
  "ordered_at": "2026-07-15T15:30:00Z",
  "reason": "Fire advancing northeast with 30 mph winds. Predicted arrival in Zone A within 4 hours.",
  "assembly_points": [
    {"name": "Chico Fairgrounds", "address": "2400 Fair St, Chico, CA 95928", "capacity": 5000}
  ],
  "estimated_evacuation_time": 90,
  "priority": 1
}
```

### Sample WeatherCondition

```json
{
  "observation_id": "d40e8400-e29b-41d4-a716-446655440333",
  "incident_id": "a10e8400-e29b-41d4-a716-446655440000",
  "location": {
    "type": "Point",
    "coordinates": [-121.6219, 39.7596]
  },
  "location_name": "RAWS Station Paradise",
  "timestamp": "2026-07-15T15:00:00Z",
  "observation_type": "current",
  "wind_speed_mph": 30,
  "wind_direction_degrees": 270,
  "wind_gust_mph": 45,
  "temperature_fahrenheit": 102,
  "relative_humidity_percent": 12,
  "fuel_moisture_percent": 4,
  "red_flag_warning": true,
  "warning_start": "2026-07-15T12:00:00Z",
  "warning_end": "2026-07-16T21:00:00Z",
  "source": "National Weather Service"
}
```

### Sample PSPSEvent

```json
{
  "psps_id": "e50e8400-e29b-41d4-a716-446655440444",
  "incident_id": "a10e8400-e29b-41d4-a716-446655440000",
  "utility_name": "PG&E",
  "event_name": "PSPS-2026-0715-BUTTE",
  "affected_counties": ["Butte", "Plumas"],
  "customer_count": 12500,
  "critical_facilities_count": 8,
  "de_energization_planned": "2026-07-15T18:00:00Z",
  "de_energization_actual": "2026-07-15T18:15:00Z",
  "restoration_estimated": "2026-07-17T12:00:00Z",
  "status": "active",
  "coordination_notes": "CAL FIRE requested PSPS due to fire proximity to transmission lines. 8 critical facilities identified for generator deployment: 2 hospitals, 3 water systems, 2 communication sites, 1 emergency operations center.",
  "resources_deployed": [
    {"type": "generator", "capacity_kw": 500, "facility": "Adventist Health Feather River"},
    {"type": "generator", "capacity_kw": 200, "facility": "Paradise Water Treatment Plant"}
  ]
}
```
