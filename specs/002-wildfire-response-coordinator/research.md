# Technology Research: Wildfire Response Coordinator

**Feature**: Wildfire Response Coordinator  
**Date**: 2026-02-02  
**Author**: Tank (Backend Dev)

## Overview

This document captures technology decisions, architectural choices, mock strategy, and risk analysis for the Wildfire Response Coordinator—a multi-agency AI coordination system for California wildfires serving CAL FIRE, Cal OES, county fire departments, and utilities during California's peak fire season.

---

## Technology Choices

### 1. Azure OpenAI Model Selection

| Decision | **GPT-4o for incident assessment and multi-agent orchestration** |
|----------|------------------------------------------------------------------|
| **Rationale** | GPT-4o provides strong reasoning for complex coordination decisions (resource allocation, evacuation prioritization). Superior function-calling for MCP tool integration (weather APIs, CAL FIRE data feeds, traffic data). Constitutional requirement: explainable reasoning for high-risk decisions per EO N-12-23. |
| **Alternatives Considered** | GPT-3.5-turbo (insufficient reasoning for resource allocation), Claude (not on Azure), rule-based system (brittle for edge cases) |
| **Trade-offs** | Higher cost per decision (~$0.02 vs $0.001 for rule-based) but critical for handling novel incident scenarios. Emergency coordination justifies cost. |
| **Performance Impact** | ~2-3s decision time at p95 for resource allocation, acceptable for non-real-time coordination decisions. |

### 2. Geospatial Platform: Azure Maps

| Decision | **Azure Maps for incident mapping, evacuation routing, proximity calculations** |
|----------|----------------------------------------------------------------------------------|
| **Rationale** | Native Azure integration, real-time traffic data, routing API for evacuation optimization. GeoJSON support for fire perimeters, evacuation zones, mutual aid region boundaries. Offline map tiles for communication outage resilience. |
| **Alternatives Considered** | Google Maps (cross-cloud complexity, higher cost), Mapbox (limited traffic data), PostGIS-only (no routing, no traffic) |
| **Trade-offs** | Azure Maps transactions cost ~$5 per 1000 routing requests. Acceptable for emergency coordination (budget: $500/month for 100k evacuations). |
| **Performance Impact** | <500ms routing calculations for 10-stop evacuation routes. Geospatial queries cached in PostGIS for repeat lookups. |

### 3. Weather Data Integration Strategy

| Decision | **National Weather Service API + NOAA Red Flag Warning RSS feeds** |
|----------|---------------------------------------------------------------------|
| **Rationale** | Authoritative federal weather data, free API access, Red Flag Warning alerts critical for fire behavior prediction. 15-minute update frequency sufficient for wildfire coordination (fire spread measured in hours, not minutes). |
| **Alternatives Considered** | Commercial weather APIs (Weather Underground, OpenWeather) for higher resolution, custom weather stations (CAL FIRE RAWS network requires integration), Azure Weather service (limited Red Flag Warning support) |
| **Trade-offs** | NWS API has no SLA (99% uptime observed), RSS parsing required for Red Flag Warnings. Acceptable for free authoritative data. |
| **Performance Impact** | Weather data cached for 15 minutes. <100ms cache hit, <2s cache miss (RSS fetch + parse). |

### 4. Traffic and Evacuation Routing

| Decision | **Azure Maps routing API + Caltrans 511 traffic data integration** |
|----------|---------------------------------------------------------------------|
| **Rationale** | Azure Maps provides base routing; Caltrans 511 API provides California highway patrol incident data (road closures, accidents). Combining both enables accurate evacuation route optimization accounting for wildfire-related closures. |
| **Alternatives Considered** | Google Maps traffic (cross-cloud), HERE Maps (cost), Azure Maps only (limited California-specific incident data) |
| **Trade-offs** | Caltrans 511 API has intermittent outages (95% uptime). Fallback: Azure Maps routing without incident data. Acceptable for best-effort optimization. |
| **Performance Impact** | <1s routing calculation with traffic. 5-minute Caltrans cache refresh (incidents change slowly). |

### 5. Resource Management Database

| Decision | **PostgreSQL with PostGIS for resource tracking and spatial queries** |
|----------|-----------------------------------------------------------------------|
| **Rationale** | PostGIS enables geospatial queries (nearest available engine, resources within 50-mile radius). PostgreSQL ACID guarantees critical for resource allocation (prevent double-assignment). JSONB for flexible resource metadata (crew size, capability ratings, equipment). |
| **Alternatives Considered** | MongoDB (weak ACID), Azure Cosmos DB (expensive for geospatial workloads), pure spatial database (ArcGIS Server - high cost) |
| **Trade-offs** | PostgreSQL + PostGIS adds operational complexity vs managed NoSQL, but geospatial query performance and ACID guarantees essential. |
| **Performance Impact** | <100ms for spatial queries (nearest 50 resources). GiST indexes on geometry columns. |

### 6. Real-Time Coordination: WebSocket Architecture

| Decision | **FastAPI WebSocket for real-time incident updates to coordinators** |
|----------|----------------------------------------------------------------------|
| **Rationale** | Incident status changes (fire size, resource deployments, evacuations) must push to coordinators immediately. WebSocket reduces polling load, enables <1s update latency. Redis pub/sub for multi-instance broadcast. |
| **Alternatives Considered** | Server-Sent Events (SSE) (no client→server messaging), long polling (high server load), SignalR (adds .NET dependency) |
| **Trade-offs** | WebSocket requires persistent connections (max 5000 per instance). Auto-scale handles load. Acceptable for coordinator count (100-500 concurrent). |
| **Performance Impact** | <500ms incident update push latency. Redis pub/sub adds ~50ms overhead. |

### 7. PSPS (Public Safety Power Shutoff) Coordination

| Decision | **MCP tool integration with PG&E, SCE, SDG&E PSPS APIs** |
|----------|-----------------------------------------------------------|
| **Rationale** | Utilities provide PSPS event APIs (affected circuits, customer counts, de-energization schedules). MCP tool pattern enables dynamic integration without hardcoded API clients. Constitutional requirement: log utility coordination for public accountability. |
| **Alternatives Considered** | Email-based coordination (not machine-readable), manual data entry (not scalable), custom API clients (brittle) |
| **Trade-offs** | Utility APIs have varying schemas (PG&E vs SCE). MCP abstraction layer required. Acceptable for multi-utility support. |
| **Performance Impact** | <2s to fetch PSPS event data. 1-hour cache (PSPS schedules change infrequently). |

---

## Architecture Decisions

### 1. Multi-Agent Pipeline Design

| Decision | **4-agent pipeline: IncidentAgent → ResourceAgent → EvacuationAgent → CoordinationAgent** |
|----------|--------------------------------------------------------------------------------------------|
| **Rationale** | Separation of concerns: IncidentAgent (lead agency mapping, mutual aid region), ResourceAgent (allocation optimization), EvacuationAgent (zone/route planning), CoordinationAgent (escalation, PSPS coordination). Enables independent Constitutional compliance checks (high-risk decisions flagged at each stage per EO N-12-23). |
| **Alternatives Considered** | 3-agent pipeline (standard pattern, but evacuation complexity justifies separate agent), monolithic agent (poor auditability), 5+ agents (over-engineered) |
| **Trade-offs** | 4-agent pipeline adds ~300ms orchestration overhead but critical for EO N-12-23 high-risk decision auditability (evacuations, resource shortages). |

### 2. Incident Command Structure Integration

| Decision | **ICS (Incident Command System) role mapping in AgencyAssignment model** |
|----------|---------------------------------------------------------------------------|
| **Rationale** | CAL FIRE and Cal OES use NIMS/ICS structure (Incident Commander, Operations Chief, Logistics Chief). System must map agents to ICS roles for human-AI collaboration. CoordinationAgent recommends, human Incident Commander approves high-risk decisions. |
| **Alternatives Considered** | Autonomous AI decision-making (Constitutional violation), flat coordination (no clear approval chain) |
| **Trade-offs** | Human-in-the-loop slows decision-making (~5-15 minutes for Incident Commander approval) but required for Constitutional Graceful Escalation and EO N-12-23 compliance. |

### 3. Offline Mode for Communication Outages

| Decision | **Cached Azure Maps tiles + local resource database sync for offline operation** |
|----------|-----------------------------------------------------------------------------------|
| **Rationale** | Wildfires often cause communication outages (cell towers down, power loss). System must function with cached maps, resource data, and last-known incident state. Offline mode enables coordination when satellite uplink only. |
| **Alternatives Considered** | Cloud-only (fails during outages), full local deployment (expensive, hard to update), hybrid (cache critical data) |
| **Trade-offs** | Offline mode limited to last-synced data (max 1-hour staleness). Weather/traffic data unavailable. Acceptable for degraded-mode operation during outages. |

### 4. Database Schema: Temporal vs Snapshot

| Decision | **Hybrid: Temporal IncidentTimeline + snapshot Resource/Incident current state** |
|----------|-----------------------------------------------------------------------------------|
| **Rationale** | Current state (Incident.size_acres, Resource.status) optimized for fast queries. IncidentTimeline preserves all changes for after-action review and Constitutional audit. Balances query performance vs auditability. |
| **Alternatives Considered** | Pure temporal (slow current-state queries), pure snapshot (no audit trail), event sourcing (complex) |
| **Trade-offs** | Dual storage increases database size (~2x) but essential for Constitutional Auditability (Principle V) and after-action reviews. |

---

## Mock Strategy

### Mock Mode Architecture

Mock mode (`USE_MOCK_SERVICES=true`) enables local development and testing without Azure credentials or external API dependencies. Critical for Labs 00-03 in workshop flow.

| Component | Mock Implementation | Data Source |
|-----------|---------------------|-------------|
| **Azure OpenAI** | Scripted incident assessments based on keywords | `backend/src/mocks/incident_responses.json` - 20 pre-assessed incident scenarios (wildfire, earthquake, flood, hazmat) |
| **Azure Maps** | Static GeoJSON polygons for mutual aid regions, hardcoded routes | `shared/data/mutual-aid-regions/regions.geojson` - 6 Cal OES regions, 10 pre-computed evacuation routes |
| **Weather API (NWS)** | Static weather data for 3 California regions, mock Red Flag Warnings | `backend/src/mocks/weather_data.json` - Northern CA, Central CA, Southern CA weather snapshots |
| **Caltrans 511 Traffic** | 5 mock road closures on I-5, Highway 99, Highway 101 | `backend/src/mocks/traffic_incidents.json` - Static incident list |
| **Utility PSPS APIs** | 2 mock PSPS events (PG&E North Bay, SCE Southern CA) | `backend/src/mocks/psps_events.json` - Pre-defined PSPS scenarios |
| **Resource Database** | 200 mock resources (50 engines, 30 hand crews, 20 aircraft, 100 support) | `shared/data/fire-stations/mock_resources.csv` - Distributed across 6 mutual aid regions |
| **WebSocket Updates** | Local broadcast (no Redis), single-instance only | In-memory pub/sub for mock mode |

### Mock Data Coverage

- **Incident Scenarios**: 20 pre-defined incidents covering wildfires (10-10,000 acres), earthquakes (4.5-7.5 magnitude), floods, hazmat
- **Resource Allocation**: 200 mock resources with realistic home stations, mutual aid regions, capability ratings
- **Evacuation Zones**: 5 pre-computed evacuation scenarios for Los Angeles, San Diego, Shasta, Butte, Riverside counties
- **Weather Conditions**: 3 regional snapshots, 2 Red Flag Warning scenarios
- **PSPS Events**: 2 scenarios covering 10k and 50k customers

### Mock Mode Limitations

- **No actual LLM reasoning**: Incident assessments keyword-matched (e.g., "wildfire" → CAL FIRE). Edge cases return generic fallback.
- **Static geospatial data**: No dynamic routing, no real-time traffic. Evacuation routes pre-computed.
- **No weather updates**: Weather data frozen at mock snapshot. Red Flag Warnings manually triggered via API.
- **Single-instance only**: WebSocket broadcast local (no Redis), cannot test multi-instance scaling.
- **Limited resource count**: 200 mock resources vs 10,000+ in production. Resource shortages not realistic.

### Verification Commands

```bash
# Start mock backend
cd backend
USE_MOCK_SERVICES=true uvicorn src.api.main:app --reload --port 8002

# Verify mock health endpoint
curl http://localhost:8002/health

# Test mock incident creation
curl -X POST http://localhost:8002/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "wildfire",
    "location": {"lat": 39.8, "lon": -121.6},
    "location_description": "5 miles NE of Paradise, Butte County",
    "size_acres": 50
  }'

# Expected mock response: Lead agency = CAL FIRE, Mutual Aid Region = I
```

---

## Risk Analysis

### Risk 1: Weather API Availability During Peak Fire Season

| Risk | **National Weather Service API has no SLA; outages during peak fire season could disable fire behavior prediction** |
|------|----------------------------------------------------------------------------------------------------------------------|
| **Impact** | HIGH - Fire behavior prediction critical for evacuation decisions and resource pre-positioning. Incorrect predictions risk lives. |
| **Likelihood** | MEDIUM - NWS API has 99% observed uptime, but peak fire season (July-October) coincides with peak API load (weather apps, news) |
| **Mitigation** | 1) 15-minute weather cache (tolerate short outages). 2) Fallback: last-known weather + static fire behavior models (wind direction from last update). 3) Manual weather entry by coordinators if API down >1 hour. 4) Constitutional escalation: flag degraded weather data in all decisions. |
| **Residual Risk** | MEDIUM - Manual weather entry slows response but acceptable for rare outages. |

### Risk 2: Geospatial Calculation Errors in Evacuation Zone Determination

| Risk | **Fire perimeter + wind direction → evacuation zone calculation may have edge cases (wind shifts, complex terrain) leading to incorrect zones** |
|------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| **Impact** | CRITICAL - Incorrect evacuation zones risk lives (under-evacuate) or cause unnecessary evacuations (over-evacuate, gridlock). EO N-12-23 high-risk use case. |
| **Likelihood** | MEDIUM - Fire behavior models inherently uncertain (10-30% error in spread prediction). Complex terrain (canyons, valleys) amplifies errors. |
| **Mitigation** | 1) Human-in-the-loop: CoordinationAgent recommends zones, Incident Commander approves/modifies. 2) Conservative over-evacuation vs under-evacuation (bias toward safety). 3) Evacuation zones versioned in IncidentTimeline for audit. 4) Post-incident review of AI evacuation accuracy vs actual fire spread. 5) Continuous model improvement based on after-action reviews. |
| **Residual Risk** | MEDIUM - Human oversight reduces but doesn't eliminate errors. Continuous improvement required. |

### Risk 3: Resource Double-Assignment During Concurrent Incidents

| Risk | **Multiple concurrent wildfires (common during peak season) may cause race conditions in resource allocation, double-assigning resources** |
|------|---------------------------------------------------------------------------------------------------------------------------------------------|
| **Impact** | HIGH - Double-assigned resources lead to no-shows, delayed response, loss of trust in system |
| **Likelihood** | LOW - PostgreSQL ACID guarantees prevent race conditions, but coordinator errors (manual overrides) possible |
| **Mitigation** | 1) Database transactions with row-level locks on Resource.status during assignment. 2) Optimistic concurrency control: version field on Resource, reject stale updates. 3) UI warnings when coordinators override system recommendations. 4) Audit log of all resource assignments for post-incident review. |
| **Residual Risk** | LOW - Database guarantees + audit trail sufficient. Coordinator training on override implications. |

### Risk 4: Utility PSPS API Schema Changes Breaking Integration

| Risk | **PG&E, SCE, SDG&E may change PSPS API schemas without notice, breaking MCP tool integration** |
|------|------------------------------------------------------------------------------------------------|
| **Impact** | MEDIUM - PSPS coordination disabled until fix deployed. Critical facilities may lack backup power during outages. |
| **Likelihood** | MEDIUM - Utilities update APIs irregularly (2-3 times/year observed). No formal API versioning or deprecation notices. |
| **Mitigation** | 1) MCP tool schema validation with graceful degradation (if schema invalid, log error + alert coordinator, continue without PSPS data). 2) Weekly automated tests against production utility APIs (detect schema changes early). 3) Manual PSPS data entry fallback via UI. 4) Quarterly coordination meetings with utility IT teams for advance notice. |
| **Residual Risk** | MEDIUM - Manual fallback acceptable for rare schema changes. Automated tests reduce discovery latency. |

### Risk 5: EO N-12-23 High-Risk Decision Auditing Overhead

| Risk | **Every evacuation and resource allocation decision flagged as high-risk requires detailed logging (reasoning, data inputs, coordinator approval). Audit log volume may overwhelm storage and query performance.** |
|------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Impact** | MEDIUM - Audit queries slow or fail, CPRA requests delayed, SB 53 compliance reporting incomplete |
| **Likelihood** | HIGH - Peak fire season may have 50-100 concurrent incidents × 10 high-risk decisions/incident/day = 1000+ audit records/day |
| **Mitigation** | 1) PostgreSQL partitioning on AuditLog.timestamp (monthly partitions, archive to cold storage after 1 year). 2) Read replicas for audit queries (separate from transactional load). 3) Materialized views for common CPRA/SB 53 reports. 4) Compression on JSON fields (reasoning, data_snapshot). |
| **Residual Risk** | LOW - Database optimization sufficient for expected audit load. Annual archival keeps hot storage manageable. |

---

## Performance Considerations

### Latency Targets

| Coordinator Action | Target p50 | Target p95 | Target p99 | Notes |
|--------------------|------------|------------|------------|-------|
| **Create incident** | <1s | <3s | <5s | Includes lead agency mapping, mutual aid region lookup, initial timeline event |
| **Request resource allocation** | <3s | <10s | <15s | Includes spatial queries (available resources within 100 miles), optimization algorithm, LLM reasoning |
| **Generate evacuation zones** | <2s | <5s | <8s | Includes fire perimeter analysis, wind direction, population density lookup, geospatial buffer calculations |
| **Optimize evacuation routes** | <1s | <3s | <5s | Azure Maps routing API (cached for repeat requests) |
| **Update weather data** | <500ms | <2s | <5s | Weather API fetch + cache write. Cache hit: <100ms. |
| **WebSocket incident update push** | <200ms | <500ms | <1s | Redis pub/sub + WebSocket send to all connected coordinators |
| **Geospatial query (nearest resources)** | <50ms | <100ms | <200ms | PostGIS GiST index on resource location |

### Caching Strategy

**Weather Cache (Redis)**:
- 15-minute TTL for weather observations
- 1-hour TTL for Red Flag Warnings (change infrequently)
- Cache key: `weather:{lat}:{lon}` rounded to 0.1° grid (reduces cache misses for nearby queries)
- Expected hit rate: 80% (coordinators query same regions repeatedly)

**Geospatial Cache (PostGIS materialized views)**:
- Mutual aid region boundaries (static, refreshed quarterly)
- Fire station locations (static, refreshed monthly)
- Evacuation assembly points (static, refreshed quarterly)
- ~1ms query time vs ~50ms for dynamic spatial joins

**Routing Cache (Redis)**:
- Evacuation routes cached by (origin, destination, traffic conditions hash)
- 5-minute TTL (traffic changes rapidly)
- Expected hit rate: 40% (repeated queries for same evacuation zones)

**Resource Status Cache (Redis pub/sub)**:
- Real-time resource status broadcast to all coordinators
- No TTL (invalidated on every status change)
- Reduces database polling from 1 query/second/coordinator to event-driven updates

### Scaling Approach

**Horizontal Scaling**:
- FastAPI backend in Azure Container Apps, auto-scale 2-10 instances based on WebSocket connection count
- Scale trigger: >500 WebSocket connections per instance (tested max: 5000/instance)
- Redis pub/sub enables multi-instance WebSocket broadcast

**Database Optimization**:
- Read replicas for audit log queries and reporting (separate from incident management load)
- Partitioning: IncidentTimeline and AuditLog partitioned by month
- Connection pooling: 20 connections/instance × 10 instances = 200 max connections (PostgreSQL supports 500)

**Geospatial Optimization**:
- PostGIS GiST indexes on all geometry columns (location, perimeter, evacuation zones)
- Spatial index selectivity: <100ms for "resources within 50-mile radius" query on 10k resources
- Pre-computed mutual aid region boundaries (avoid expensive polygon intersections)

**Cost Projection**:
- Baseline (10 concurrent incidents): ~$1500/month (Azure OpenAI $400, Azure Maps $300, compute $500, storage $300)
- Peak (100 concurrent incidents, peak fire season): ~$5000/month (more compute instances, higher Azure Maps usage)
- Emergency budget allocation: $10k/month for catastrophic fire season (Camp Fire-scale events)

---

## Dependencies and Integration Points

### External Azure Services
- **Azure OpenAI**: GPT-4o for multi-agent orchestration
- **Azure Maps**: Geospatial platform for routing, proximity, mapping
- **Azure Monitor**: Application Insights for performance monitoring, Constitutional compliance dashboards
- **Azure Entra ID**: Authentication for CAL FIRE, Cal OES, county coordinators

### External APIs (Non-Azure)
- **National Weather Service**: Weather observations, Red Flag Warnings (free, no auth)
- **NOAA RSS**: Red Flag Warning alerts (free, no auth)
- **Caltrans 511**: California traffic incidents, road closures (free, API key required)
- **PG&E PSPS API**: Public Safety Power Shutoff events (free, API key required)
- **SCE PSPS API**: Southern California Edison PSPS events (free, API key required)
- **SDG&E PSPS API**: San Diego Gas & Electric PSPS events (free, API key required)

### California State Systems
- **CAL FIRE Incident Database**: MCP tool integration for historical incident data
- **Cal OES Emergency Operations Center**: WebSocket integration for real-time coordination (future)
- **County Emergency Operations Centers**: Email/phone notifications for escalations (58 counties)

### Workshop Integration
- **Labs 00-03**: Mock mode, no Azure or external API dependencies
- **Lab 04+**: Azure credentials required, Bicep deployment to Azure Container Apps, external API keys for weather/traffic/PSPS

---

## Open Questions and Future Research

1. **Machine learning for fire behavior prediction**: Could ML models improve fire spread prediction accuracy vs rule-based models? Requires training data from historical fires.
2. **Drone integration for real-time perimeter mapping**: Could CAL FIRE drones provide real-time fire perimeter updates via API? Requires drone telemetry integration.
3. **Satellite imagery for damage assessment**: Could Azure AI Vision analyze satellite imagery for structure damage counts? Requires high-resolution satellite access.
4. **Automated resource pre-positioning**: Could the system proactively deploy resources before Red Flag Warning fires start? Requires predictive modeling and human approval workflows.
5. **Cross-state mutual aid coordination**: Could the system coordinate with Oregon, Nevada, Arizona for border fires? Requires interstate API integration and legal agreements.

---

**Last Updated**: 2026-02-02  
**Next Review**: After pilot deployment (Q3 2026, pre-fire-season)
