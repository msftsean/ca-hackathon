# Feature Specification: Wildfire Response Coordinator

**Feature Branch**: `002-wildfire-response-coordinator`  
**Created**: 2026-02-02  
**Status**: Draft  
**Agency**: CAL FIRE, California Governor's Office of Emergency Services (Cal OES)  
**Problem**: California's #1 emergency threat - multi-agency coordination complexity  

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Incident Assessment and Lead Agency Mapping (Priority: P1)

An emergency coordinator creates a new wildfire incident in the system by providing incident type, location, and initial severity. The Wildfire Response Coordinator automatically identifies the lead agency (Wildfire→CAL FIRE, Earthquake→Cal OES, Flood→DWR, HazMat→CHP), determines the Cal OES mutual aid region (6 regions statewide), and sets up the incident command structure. This establishes the coordination framework for all subsequent response activities.

**Why this priority**: Core foundation for all emergency coordination. Without accurate lead agency identification and mutual aid region mapping, resource allocation and multi-agency coordination cannot function. Must work independently to deliver baseline incident management value.

**Independent Test**: Can be fully tested by creating various incident types (wildfire, earthquake, flood, hazmat) at different California locations and verifying correct lead agency and mutual aid region assignment. Delivers immediate value by automating initial incident classification.

**Acceptance Scenarios**:

1. **Given** a coordinator creates a wildfire incident in Shasta County, **When** the incident is submitted, **Then** the system assigns CAL FIRE as lead agency and identifies Mutual Aid Region I (Northern California)
2. **Given** a coordinator creates an earthquake incident in Los Angeles, **When** the incident is submitted, **Then** the system assigns Cal OES as lead agency and identifies Mutual Aid Region VI (Southern California)
3. **Given** a coordinator creates a flood incident near Sacramento River, **When** the incident is submitted, **Then** the system assigns DWR (Department of Water Resources) as lead agency and identifies Mutual Aid Region III (Inland)
4. **Given** a coordinator creates a hazmat incident on I-5, **When** the incident is submitted, **Then** the system assigns CHP as lead agency and identifies the appropriate mutual aid region based on location
5. **Given** an incident spans multiple counties, **When** the incident boundaries are defined, **Then** the system identifies all affected mutual aid regions and coordinates cross-region response

---

### User Story 2 - Resource Allocation and Deployment Recommendations (Priority: P2)

Once a wildfire incident is established, the system recommends resource deployment based on fire size, terrain, weather conditions (wind speed, humidity, Red Flag Warnings), and available resources in the mutual aid region. The system tracks resource status (available, deployed, en route, out of service) and suggests optimal deployment to maximize firefighting effectiveness while maintaining coverage for other potential incidents.

**Why this priority**: Critical for effective wildfire response but depends on P1 foundation (incident and lead agency must be established first). Resource allocation is a key differentiator for AI-assisted coordination but cannot function without incident assessment.

**Independent Test**: Can be tested by creating wildfire incidents of varying sizes and conditions, then verifying resource recommendations match expected deployment patterns based on CAL FIRE protocols. Delivers standalone value by optimizing resource utilization.

**Acceptance Scenarios**:

1. **Given** a 50-acre wildfire in steep terrain with high winds, **When** resource allocation is requested, **Then** the system recommends air tankers, hand crews, and bulldozers based on terrain accessibility and fire behavior
2. **Given** a Red Flag Warning is active in the region, **When** resource allocation is calculated, **Then** the system reserves resources for potential new starts and recommends mutual aid from adjacent regions
3. **Given** multiple concurrent wildfires in the same mutual aid region, **When** resource allocation is requested, **Then** the system prioritizes resources based on threat to life and structures, fire behavior, and strategic importance
4. **Given** a resource unit becomes unavailable (out of service), **When** the resource status is updated, **Then** the system recalculates deployment recommendations and identifies replacement resources from mutual aid
5. **Given** a wildfire grows beyond initial attack capacity, **When** extended attack is triggered, **Then** the system recommends escalation to Type 1 or Type 2 Incident Management Team and requests additional mutual aid

---

### User Story 3 - Evacuation Planning and Route Optimization (Priority: P3)

The system generates evacuation zone recommendations based on fire perimeter, predicted fire behavior (wind direction, spread rate), population density, and infrastructure. It optimizes evacuation routes considering road closures, traffic capacity, and assembly points (fairgrounds, schools, parking lots). The system integrates with Azure Maps to visualize evacuation zones and routes, helping coordinators make rapid decisions to protect lives.

**Why this priority**: High impact for life safety but requires P1 (incident assessment) and P2 (resource allocation) to be working first. Evacuation planning depends on understanding fire behavior and resource deployment. Building this before the foundation would be premature.

**Independent Test**: Can be tested by defining fire perimeters and wind conditions, then verifying evacuation zone recommendations and route optimization match expected patterns. Delivers standalone value by automating life safety planning.

**Acceptance Scenarios**:

1. **Given** a wildfire with west-to-east wind direction, **When** evacuation planning is requested, **Then** the system identifies downwind communities as high-priority evacuation zones
2. **Given** a road closure on the primary evacuation route, **When** evacuation routes are calculated, **Then** the system identifies alternative routes and updates traffic flow capacity estimates
3. **Given** a community with elderly population and limited mobility, **When** evacuation is recommended, **Then** the system flags the need for accessible transportation and extended evacuation time
4. **Given** an evacuation order is issued, **When** the order is broadcast, **Then** the system integrates with emergency alert systems (Wireless Emergency Alerts, Emergency Alert System) and provides multi-language notifications
5. **Given** evacuation routes converge at a bottleneck, **When** traffic modeling is performed, **Then** the system recommends staggered evacuation timing by zone to prevent gridlock

---

### User Story 4 - Weather Integration and Red Flag Warning Response (Priority: P4)

The system continuously ingests weather data (wind speed, wind direction, humidity, temperature) and National Weather Service Red Flag Warnings. When conditions deteriorate, the system alerts coordinators, adjusts fire behavior predictions, updates resource recommendations, and suggests proactive resource pre-positioning. This integration enables anticipatory response rather than reactive response.

**Why this priority**: Valuable for proactive coordination but depends on P1-P3 working correctly. Weather integration enhances the quality of decisions made by earlier features but is not required for basic incident management to function.

**Independent Test**: Can be tested by injecting simulated weather data and Red Flag Warnings, then verifying appropriate alerts, updated fire behavior predictions, and resource pre-positioning recommendations.

**Acceptance Scenarios**:

1. **Given** wind speed increases above 25 mph, **When** weather data is updated, **Then** the system alerts coordinators and recommends grounding aircraft until conditions improve
2. **Given** a Red Flag Warning is issued for the region, **When** the warning is ingested, **Then** the system recommends resource pre-positioning in high-risk areas and increased staffing for initial attack
3. **Given** humidity drops below 15%, **When** weather conditions update, **Then** the system flags extreme fire behavior risk and suggests proactive evacuations in wildland-urban interface areas
4. **Given** wind direction shifts from west to north, **When** wind direction changes, **Then** the system updates fire spread predictions and recalculates evacuation zone priorities
5. **Given** weather forecast predicts Santa Ana winds in 24 hours, **When** forecast is received, **Then** the system recommends advance coordination with utilities for Public Safety Power Shutoff (PSPS) and pre-positioning of resources

---

### User Story 5 - Utility Coordination and PSPS Integration (Priority: P5)

The system coordinates with California's major utilities (PG&E, Southern California Edison, San Diego Gas & Electric) for Public Safety Power Shutoff (PSPS) planning. When wildfires threaten power infrastructure or PSPS is planned, the system identifies affected communities, coordinates resource deployment to support de-energized areas (backup power for critical facilities), and tracks power restoration timing to inform demobilization decisions.

**Why this priority**: Important for modern wildfire response (PSPS is a major factor in California wildfires) but should be the last feature built. PSPS coordination enhances P1-P4 but cannot function without the incident management, resource allocation, and evacuation planning foundations.

**Independent Test**: Can be tested by simulating PSPS events and verifying coordination workflows, affected community identification, and resource deployment for de-energized areas.

**Acceptance Scenarios**:

1. **Given** a wildfire threatens power lines, **When** PSPS is considered, **Then** the system identifies affected circuits, estimates number of customers impacted, and recommends coordination with utility
2. **Given** PG&E plans PSPS in high-fire-threat areas, **When** PSPS notification is received, **Then** the system identifies critical facilities (hospitals, water systems, communication sites) requiring backup power and recommends generator deployment
3. **Given** a wildfire burns through de-energized area, **When** fire containment is achieved, **Then** the system coordinates with utility on safe timing for power restoration and identifies hazards (burned poles, downed lines)
4. **Given** PSPS affects multiple counties, **When** coordination is required, **Then** the system identifies lead county, mutual aid resources for generator deployment, and communication plans for affected residents
5. **Given** a utility requests emergency responder support during PSPS restoration, **When** the request is received, **Then** the system identifies available CAL FIRE crews for line safety patrols and coordinates deployment

---

### Edge Cases

- What happens when an incident type is ambiguous or involves multiple hazards (e.g., wildfire caused by earthquake, flooding from firefighting water)?
- How does the system handle incidents that span multiple mutual aid regions or cross state borders (Oregon, Nevada, Arizona)?
- What happens when all resources in a mutual aid region are deployed and no mutual aid is available from adjacent regions?
- How does the system handle conflicting priorities between life safety and structure protection?
- What happens when weather data is unavailable or significantly delayed?
- How does the system handle incidents during communication outages or degraded network connectivity?
- What happens when utilities refuse or delay PSPS implementation despite system recommendations?
- How does the system handle evacuations for areas with single-route access (canyon communities, rural areas)?
- What happens when predicted fire behavior differs significantly from actual fire behavior?
- How does the system handle coordination with federal agencies (US Forest Service, National Park Service, BLM) on federal lands?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST classify incident types (wildfire, earthquake, flood, hazmat, multi-hazard) based on coordinator input
- **FR-002**: System MUST automatically assign lead agency based on incident type (Wildfire→CAL FIRE, Earthquake→Cal OES, Flood→DWR, HazMat→CHP)
- **FR-003**: System MUST identify Cal OES mutual aid region (I-VI) based on incident location coordinates
- **FR-004**: System MUST track resource inventory including type, unit name, home location, current status, and mutual aid region
- **FR-005**: System MUST support resource status tracking (available, deployed, en route, out of service, on order)
- **FR-006**: System MUST recommend resource deployment based on fire size, terrain, weather, and available resources
- **FR-007**: System MUST calculate evacuation zones based on fire perimeter, wind direction, fire spread rate, and population density
- **FR-008**: System MUST optimize evacuation routes considering road closures, traffic capacity, and assembly points
- **FR-009**: System MUST integrate with Azure Maps for geospatial visualization of incidents, resources, and evacuation zones
- **FR-010**: System MUST ingest real-time weather data (wind speed, wind direction, humidity, temperature) from weather APIs
- **FR-011**: System MUST ingest National Weather Service Red Flag Warnings and Fire Weather Watches
- **FR-012**: System MUST alert coordinators when weather conditions exceed critical thresholds (wind >25 mph, humidity <15%)
- **FR-013**: System MUST update fire behavior predictions when wind direction or speed changes significantly
- **FR-014**: System MUST identify PSPS-affected circuits and communities when wildfire threatens power infrastructure
- **FR-015**: System MUST coordinate resource deployment for critical facilities (hospitals, water systems) during PSPS events
- **FR-016**: System MUST track utility power restoration timing and coordinate with demobilization planning
- **FR-017**: System MUST support multi-agency collaboration with CAL FIRE, Cal OES, county fire departments, CHP, and utilities
- **FR-018**: System MUST log all incident decisions, resource deployments, and agency coordination per Constitutional Auditability requirements
- **FR-019**: System MUST support incident timeline visualization showing key events, decisions, and resource deployments
- **FR-020**: System MUST integrate with emergency alert systems (Wireless Emergency Alerts, Emergency Alert System) for evacuation notifications
- **FR-021**: System MUST support multi-language evacuation notifications per California Language Access requirements
- **FR-022**: System MUST detect and escalate coordination issues requiring human decision-making (conflicting priorities, resource shortages)
- **FR-023**: System MUST comply with Executive Order N-12-23 high-risk use case reporting requirements
- **FR-024**: System MUST support offline mode with cached maps and resource data for communication outages

### Key Entities

- **Incident**: A wildfire or emergency event requiring multi-agency coordination, including incident ID, type, location, severity, lead agency, status, affected mutual aid regions, and timeline
- **Resource**: A firefighting or emergency resource (engine, crew, aircraft, dozer, command vehicle), including resource ID, type, unit name, home station, current status, assigned incident, and mutual aid region
- **EvacuationZone**: A geographic area requiring evacuation, including zone ID, boundaries, population estimate, evacuation status, routes, and assembly points
- **WeatherCondition**: Real-time or forecast weather data, including location, timestamp, wind speed, wind direction, humidity, temperature, Red Flag Warning status
- **AgencyAssignment**: A record of agency involvement in an incident, including incident ID, agency, role (lead, support, mutual aid), resources committed, and contact information
- **PSPSEvent**: A Public Safety Power Shutoff event, including PSPS ID, utility, affected circuits, customer count, de-energization time, restoration time, and coordination status

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Incident assessment correctly identifies lead agency and mutual aid region in 100% of standard incident types
- **SC-002**: Resource allocation recommendations are generated within 10 seconds of incident creation or update
- **SC-003**: Evacuation zone recommendations account for wind direction, fire spread, and population density in 95%+ of scenarios
- **SC-004**: Evacuation route optimization reduces estimated evacuation time by 20%+ compared to default routes in simulated scenarios
- **SC-005**: Weather data integration updates fire behavior predictions within 5 minutes of significant weather changes
- **SC-006**: Red Flag Warning alerts are delivered to coordinators within 2 minutes of National Weather Service issuance
- **SC-007**: PSPS-affected community identification is 98%+ accurate compared to utility service territory maps
- **SC-008**: System maintains operational capability (offline mode) during simulated communication outages
- **SC-009**: Multi-agency coordination reduces incident command setup time by 30% in pilot incidents
- **SC-010**: Audit logs capture all required information (incident data, resource deployments, decisions, weather conditions) for 100% of incidents per Constitutional requirements
- **SC-011**: System response time remains under 3 seconds for 95% of coordinator actions (incident creation, resource assignment, evacuation planning)
- **SC-012**: Executive Order N-12-23 high-risk use case reporting requirements are met for 100% of life-safety decisions
