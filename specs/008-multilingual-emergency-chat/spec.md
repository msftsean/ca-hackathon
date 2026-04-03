# Feature Specification: Multilingual Emergency Chatbot

**Feature Branch**: `008-multilingual-emergency-chat`  
**Created**: 2026-04-02  
**Status**: Draft  
**Agency**: California Governor's Office of Emergency Services (Cal OES)  
**Compliance**: EO N-12-23, Envision 2026 Goal 1, ADA/WCAG AA, FCC Emergency Alert System requirements  
**Input**: Real-time emergency information in 70+ languages via Azure Translator, with evacuation orders, shelter locator, air quality alerts, and SMS access for low-bandwidth scenarios

## Problem Statement

During the 2025 Los Angeles fires, non-English-speaking residents could not access critical evacuation orders, shelter information, or air quality alerts in their native languages. Emergency communication systems were English-only, creating life-threatening delays for California's diverse population. Traditional phone-based emergency systems were overwhelmed, with wait times exceeding 2 hours. Residents in rural areas or with slow internet connections could not access web-based emergency dashboards.

## Vision

Provide a lightweight, multilingual emergency information assistant that delivers real-time alerts, evacuation orders, shelter locations, and air quality data in 70+ languages via Azure Translator. The system works on low-bandwidth connections and supports SMS access for residents without smartphones or reliable internet. Architecture is deliberately simple — single-agent design with Azure AI Search for emergency knowledge base and Azure Translator for real-time translation — to ensure resilience during infrastructure strain.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Emergency Info Lookup by Location (Priority: P1)

A resident enters their address or ZIP code and receives current emergency alerts (fire, flood, earthquake, air quality) relevant to their location, automatically translated to their selected language.

**Why this priority**: This is the core life-safety capability. If only this ships, residents can get location-specific emergency information in their language, which is the primary use case during active disasters.

**Independent Test**: Can be fully tested by entering a ZIP code, selecting Spanish, and verifying emergency alerts are returned in Spanish within 3 seconds.

**Acceptance Scenarios**:

1. **Given** a resident visits the emergency chatbot page, **When** they enter ZIP code 90001, **Then** the system retrieves active emergency alerts for that area and displays them in English by default.
2. **Given** a resident selects Spanish from the language dropdown, **When** they enter their address "123 Main St, Los Angeles, CA", **Then** all emergency alerts are translated to Spanish via Azure Translator and displayed with alert type, severity, issued time, and expiration.
3. **Given** there are no active alerts for a location, **When** a resident searches ZIP 95832, **Then** the system responds "No active emergency alerts for your area. Last checked: [timestamp]" in their selected language.
4. **Given** a resident enters an invalid ZIP code, **When** the system validates the input, **Then** it prompts "Please enter a valid California ZIP code" in the selected language without crashing.
5. **Given** multiple alert types are active (fire + air quality + evacuation), **When** displayed, **Then** they are sorted by severity (urgent → warning → advisory) with color-coded badges.

---

### User Story 2 - Multi-Language Support via Azure Translator (Priority: P2)

A resident selects their preferred language from 70+ options. All emergency content — alerts, evacuation orders, shelter info, air quality guidance — is automatically translated via Azure Translator with translation caching for performance.

**Why this priority**: Language access is the defining feature of this accelerator. Without multi-language support, this is just another emergency dashboard.

**Independent Test**: Can be tested by selecting Tagalog, entering a location with active alerts, and verifying all content is translated to Tagalog with correct alert metadata preserved.

**Acceptance Scenarios**:

1. **Given** a resident clicks the language selector, **When** the dropdown opens, **Then** it displays 70+ languages sorted alphabetically with native script (e.g., "中文 (Chinese)", "Español (Spanish)", "Tiếng Việt (Vietnamese)").
2. **Given** a resident selects Vietnamese, **When** they ask "Where is the nearest shelter?", **Then** the query is translated to English for processing, the response is generated, then translated back to Vietnamese before display.
3. **Given** an emergency alert is displayed in Korean, **When** the resident switches to Armenian mid-session, **Then** all previously displayed content is re-translated to Armenian and the page updates without requiring a refresh.
4. **Given** translation fails (Azure Translator API down), **When** an error occurs, **Then** the system falls back to English with a message "Translation temporarily unavailable. Content shown in English" in the last-known selected language (cached from previous successful translation).
5. **Given** a resident's browser language is set to Spanish, **When** they first visit the page, **Then** the language selector defaults to Spanish and all content loads in Spanish automatically.
6. **Given** emergency alerts contain technical terms (Air Quality Index, PM2.5, evacuation zone), **When** translated, **Then** terminology is preserved correctly (e.g., "AQI" remains "AQI", not translated as "air quality indicator" which could cause confusion).

---

### User Story 3 - Evacuation Order Check (Priority: P3)

A resident checks if their address or zone is under an active evacuation order (mandatory or voluntary). The system returns evacuation status, recommended routes, and nearest shelter locations.

**Why this priority**: Evacuation status is time-critical and directly impacts life safety. This can function independently of other features.

**Independent Test**: Can be tested by entering an address in an active evacuation zone and verifying the system returns evacuation order details, routes, and shelter recommendations.

**Acceptance Scenarios**:

1. **Given** a resident enters an address under mandatory evacuation, **When** the system checks evacuation orders, **Then** it displays "MANDATORY EVACUATION — Leave immediately" with recommended evacuation routes, closure information, and nearest shelter.
2. **Given** a resident is in a voluntary evacuation zone, **When** they check status, **Then** the system displays "VOLUNTARY EVACUATION — Prepare to leave. Vulnerable populations (elderly, disabled, children) should evacuate now" with shelter options.
3. **Given** a resident is NOT in an evacuation zone, **When** they check their address, **Then** the system confirms "Your area is NOT under evacuation order" and provides the nearest active evacuation zone boundary.
4. **Given** an evacuation order has recommended routes, **When** displayed, **Then** the system shows a list of open routes, closed roads, and traffic conditions (if available).
5. **Given** a resident asks about evacuation order timing, **When** the order was issued, **Then** the system displays "Issued: [datetime], Expires: [datetime or 'Until further notice']" with last-updated timestamp.

---

### User Story 4 - Shelter Locator with Capacity and Services (Priority: P4)

A resident searches for nearby emergency shelters. The system returns a list of open shelters within 25 miles, sorted by distance, with current capacity, services offered (pet-friendly, ADA-accessible, medical support), and contact information.

**Why this priority**: Shelter location is critical during evacuations and disasters. This can be tested and deployed independently.

**Independent Test**: Can be tested by entering a location and verifying the system returns shelters sorted by distance with capacity, services, and contact info.

**Acceptance Scenarios**:

1. **Given** a resident searches for shelters near ZIP 90210, **When** the system queries the shelter database, **Then** it returns all open shelters within 25 miles sorted by distance with name, address, capacity status (e.g., "150/200 capacity"), and hours.
2. **Given** a shelter is at capacity, **When** displayed, **Then** it shows "AT CAPACITY" with a suggestion to call ahead or try the next nearest shelter.
3. **Given** a resident needs ADA-accessible facilities, **When** they filter by accessibility, **Then** only shelters with wheelchair access, accessible restrooms, and medical support are shown.
4. **Given** a resident has pets, **When** they ask about pet-friendly shelters, **Then** the system filters for shelters accepting pets and displays pet policies (crate required, vaccination proof, etc.).
5. **Given** a shelter has special services (medical clinic, mental health support, food service), **When** displayed, **Then** services are listed with availability times (e.g., "Medical clinic: 8am-8pm, Mental health counseling: By appointment").
6. **Given** no shelters are open within 25 miles, **When** the search fails, **Then** the system expands the radius to 50 miles and informs the user "No shelters within 25 miles. Showing results within 50 miles."

---

### User Story 5 - Air Quality Alerts and Health Guidance (Priority: P5)

A resident checks current air quality for their location. The system returns AQI (Air Quality Index), pollutant levels (PM2.5, PM10, ozone), health risk category, and recommended actions (stay indoors, wear N95, avoid outdoor activity).

**Why this priority**: Air quality is critical during wildfires and industrial incidents. This can function as a standalone feature.

**Independent Test**: Can be tested by entering a location and verifying the system returns current AQI with health guidance in the selected language.

**Acceptance Scenarios**:

1. **Given** a resident enters ZIP 94102, **When** the system retrieves air quality data, **Then** it displays current AQI (e.g., "AQI 152 - Unhealthy") with color-coded badge (green/yellow/orange/red/purple/maroon).
2. **Given** AQI is in "Unhealthy" range (151-200), **When** displayed, **Then** health guidance states "Everyone should reduce outdoor activity. People with respiratory conditions should stay indoors."
3. **Given** AQI is in "Hazardous" range (301+), **When** displayed, **Then** health guidance states "STAY INDOORS. Avoid all outdoor activity. Use N95 masks if you must go outside. Close windows and use air purifiers."
4. **Given** air quality data includes pollutant breakdown, **When** shown, **Then** the system displays PM2.5, PM10, and ozone levels individually with thresholds (e.g., "PM2.5: 85 µg/m³ (Unhealthy)").
5. **Given** air quality forecast is available, **When** a resident asks about the next 24 hours, **Then** the system shows hourly AQI forecast with trend (improving/worsening).
6. **Given** air quality data is unavailable for a location, **When** the lookup fails, **Then** the system responds "Air quality data unavailable for this location. Nearest monitoring station: [name, 15 miles away]" and suggests checking statewide resources.

---

### User Story 6 - SMS Access for Low-Bandwidth Scenarios (Priority: P6)

A resident without smartphone or internet access sends an SMS to a designated emergency number. The system responds via SMS with emergency alerts, shelter locations, and air quality info in their requested language.

**Why this priority**: SMS ensures access during infrastructure failures and for digitally underserved populations. This is a separate channel but critical for equity.

**Independent Test**: Can be tested by sending an SMS "Shelters near 90001 in Spanish" and verifying the system responds via SMS with shelter list in Spanish.

**Acceptance Scenarios**:

1. **Given** a resident texts "Alerts for 95814" to the emergency SMS number, **When** the system processes the request, **Then** it responds via SMS with active alerts in plain text: "ALERT: Flood Warning until 8pm. Avoid low-lying areas. More: [short link]"
2. **Given** a resident texts "Shelters 90210 Spanish", **When** the system detects language request, **Then** the response is translated to Spanish: "Refugio más cercano: Cruz Roja, 123 Main St, 5 millas. Capacidad: 100/150. Tel: 555-1234."
3. **Given** a resident texts "Air quality 94105", **When** air quality data is retrieved, **Then** the SMS response includes "AQI 165 Unhealthy. Limit outdoor activity. PM2.5 high. More: [link]"
4. **Given** the SMS query is unclear ("help me"), **When** the system cannot determine intent, **Then** it responds with a menu: "Reply with: 1=Alerts, 2=Shelters, 3=Air Quality, 4=Evacuation. Include ZIP code."
5. **Given** SMS volume spikes during a major incident, **When** rate limits are hit, **Then** the system queues messages and responds "High volume. Your request will be processed within 5 minutes" to manage expectations.
6. **Given** a resident texts a non-English query ("¿Dónde están los refugios?"), **When** Azure Translator detects the language, **Then** the system processes the request and responds in the detected language.

---

### User Story 7 - Low-Bandwidth Web Mode (Priority: P7)

A resident on a slow or unstable internet connection accesses the chatbot. The system detects low bandwidth and serves a lightweight, server-side-rendered version with minimal JavaScript and optimized images.

**Why this priority**: During emergencies, cellular networks are often congested. Low-bandwidth mode ensures access for all residents regardless of connection quality.

**Independent Test**: Can be tested by throttling network to 2G speeds and verifying the page loads in under 5 seconds with core functionality intact.

**Acceptance Scenarios**:

1. **Given** a resident's connection speed is below 100 kbps, **When** the page loads, **Then** the system serves a no-JS HTML version with server-side rendering and text-only content (no maps, no heavy images).
2. **Given** the resident is on low-bandwidth mode, **When** they enter a ZIP code, **Then** the form submits to the server, the page refreshes with results, and no AJAX or client-side rendering is used.
3. **Given** low-bandwidth mode is active, **When** emergency alerts are displayed, **Then** color-coded badges are replaced with text indicators ("🔴 URGENT", "🟡 WARNING") that work without CSS.
4. **Given** a resident switches from low-bandwidth to normal mode (connection improves), **When** detected, **Then** the system displays a banner "Your connection has improved. Click here to switch to full version" without forcing the switch.
5. **Given** the low-bandwidth page includes critical information, **When** rendered, **Then** total page size is under 50 KB and loads in under 5 seconds on 2G.

---

### Edge Cases

- **Simultaneous emergencies**: What happens when a location has fire, flood, and air quality alerts active at once? → Display all alerts sorted by severity with clear visual separation and timestamps.
- **Translation cache expiration**: How does the system handle stale translations when alert content is updated? → Cache includes content hash; cache miss triggers re-translation on next request.
- **Language detection failure**: What if a resident texts in a language Azure Translator can't detect? → System defaults to English and responds "Reply with your language (e.g., 'Spanish', 'Vietnamese') for translated responses."
- **Shelter capacity data lag**: What if shelter capacity info is outdated and a resident arrives at a full shelter? → Display last-updated timestamp with all shelter data: "Capacity as of 2:30pm. Call ahead to confirm: [phone]."
- **ZIP code border cases**: What if a resident is on the border of two ZIP codes with different alert statuses? → Query both ZIP codes and return alerts for both with clarification: "Alerts for 90001 and neighboring 90002."
- **SMS character limits**: How does the system handle long emergency messages that exceed 160 characters? → Split into multi-part SMS with clear part indicators: "(1/3) EVACUATION ALERT..." or provide short link to full details.
- **Non-California locations**: What if a resident enters an out-of-state ZIP code? → Respond "This service covers California only. For [state] emergency info, visit [link]."
- **Historical alert lookup**: What if a resident asks about a previous emergency? → System only shows active alerts; for historical data, provide link to Cal OES archive: "For past alerts, visit [caloes.ca.gov/archive]."
- **Translation of proper nouns**: How are location names (street names, city names) handled in translation? → Proper nouns are excluded from translation (e.g., "Santa Monica Boulevard" stays "Santa Monica Boulevard" in all languages, not "Bulevar Santa Mónica").
- **Accessibility on low-bandwidth mode**: Does low-bandwidth mode still meet WCAG AA? → Yes — semantic HTML, alt text for critical images, skip links, keyboard navigation all preserved in no-JS version.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST retrieve emergency alerts for a given address or ZIP code from Cal OES data sources and display alerts sorted by severity.
- **FR-002**: System MUST support 70+ languages via Azure Translator with automatic translation of all emergency content (alerts, evacuation orders, shelter info, air quality guidance).
- **FR-003**: System MUST cache translated content with content hash to avoid redundant translation API calls and reduce latency.
- **FR-004**: System MUST check evacuation order status for a given address and return order type (mandatory/voluntary), issued time, recommended routes, and nearest shelters.
- **FR-005**: System MUST locate emergency shelters within 25 miles (expandable to 50 miles) with current capacity, services (ADA, pets, medical), hours, and contact info.
- **FR-006**: System MUST retrieve air quality data (AQI, PM2.5, PM10, ozone) for a given location and provide health risk category and recommended actions.
- **FR-007**: System MUST accept SMS queries, process location/language requests, and respond via SMS with emergency info in under 160 characters or multi-part messages.
- **FR-008**: System MUST detect connection speed and serve low-bandwidth mode (server-side rendering, no JavaScript, <50 KB page size) when bandwidth is below threshold.
- **FR-009**: System MUST preserve proper nouns (street names, city names, shelter names) during translation to avoid confusion.
- **FR-010**: System MUST display last-updated timestamps for all emergency data (alerts, shelter capacity, air quality) to inform residents of data freshness.
- **FR-011**: System MUST default to the resident's browser language or allow manual language selection with persistence across session.
- **FR-012**: System MUST degrade gracefully when Azure Translator is unavailable, falling back to English-only mode with notification to users.
- **FR-013**: System MUST restrict queries to California locations and provide appropriate messaging for out-of-state ZIP codes.
- **FR-014**: System MUST work on low-bandwidth connections (<100 kbps) with core functionality intact (alert lookup, shelter search, air quality check).
- **FR-015**: System MUST meet WCAG AA accessibility standards in both full and low-bandwidth modes, including keyboard navigation and screen reader support.

### Key Entities

- **EmergencyAlert**: Represents an active alert (fire, flood, earthquake, air quality) with alert ID, type, severity, affected area, message, issued time, expiration, and source agency.
- **EvacuationOrder**: Tracks evacuation orders with order ID, zone/area, status (mandatory/voluntary), issued time, recommended routes, road closures, and associated shelter IDs.
- **Shelter**: Stores shelter information with shelter ID, name, address, capacity (current/max), services (ADA, pets, medical), hours, contact phone, and last capacity update time.
- **AirQualityReport**: Contains air quality data for a location with AQI, pollutant breakdown (PM2.5, PM10, ozone), health risk category, guidance, forecast, and monitoring station source.
- **TranslationCache**: Caches translated content with content hash (MD5), source language, target language, translated text, and cache timestamp to reduce API calls.
- **SMSSession**: Tracks SMS interactions with session ID, phone number (hashed for privacy), selected language, last message, location context, and session creation time.
- **Location**: Represents a California location with address, ZIP code, coordinates (lat/lon), county, and associated alert zones for rapid alert lookup.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Residents can retrieve location-specific emergency alerts in their selected language in under 3 seconds for 95% of requests.
- **SC-002**: System successfully translates emergency content to 70+ languages with 95%+ accuracy (verified via human review of sample translations).
- **SC-003**: Evacuation order lookups return current status, routes, and shelters in under 2 seconds for 95% of requests.
- **SC-004**: Shelter searches return sorted results with capacity and services info in under 3 seconds for 90% of queries.
- **SC-005**: Air quality lookups return current AQI and health guidance in under 2 seconds for 95% of requests.
- **SC-006**: SMS responses are delivered within 10 seconds for 90% of queries, even during high-volume incidents.
- **SC-007**: Low-bandwidth mode pages load in under 5 seconds on 2G connections (100 kbps) with core functionality intact.
- **SC-008**: System handles 10,000+ concurrent users during major incidents without degradation (tested via load testing).
- **SC-009**: Zero translation failures result in content not being displayed; all failures degrade gracefully to English with notification.
- **SC-010**: 90%+ of residents report the system helped them access critical emergency information in post-incident surveys.
- **SC-011**: System meets WCAG AA standards in automated accessibility audits (Axe, Lighthouse) with zero critical violations.
- **SC-012**: Translation cache reduces API calls by 60%+ during high-traffic events (e.g., same alert translated to 20 languages cached after first request).
