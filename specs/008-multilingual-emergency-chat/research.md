# Research & Technology Decisions: Multilingual Emergency Chatbot

**Feature**: 008-multilingual-emergency-chat  
**Date**: 2026-04-02  
**Author**: Neo (Security Specialist)  
**Status**: Approved

This document captures the technology choices, architectural decisions, mock strategy, and risk analysis for the Multilingual Emergency Chatbot accelerator.

---

## Technology Choices

### Azure Translator for 70+ Languages

| **Decision** | **Rationale** | **Alternatives Considered** |
|--------------|---------------|----------------------------|
| **Azure Translator** with caching | Supports 70+ languages including Spanish, Chinese, Vietnamese, Tagalog, Korean, Armenian — covers 95% of CA non-English speakers. Integrated with Azure ecosystem. | Google Translate (vendor lock-in), LibreTranslate (lower quality), AWS Translate (cross-cloud complexity) |
| **Translation caching** (Redis with 24-hour TTL) | Emergency alerts rarely change within 24 hours. Cache hit rate target: 60%+. Reduces API costs by ~$800/month. | No caching (expensive), longer TTL (stale data risk), CDN caching (PII concerns) |
| **Proper noun exclusion list** | California city names, street names, shelter names should NOT be translated (e.g., "Los Angeles" stays "Los Angeles", not "Los Ángeles"). | Translate everything (confusing), manual list (maintenance burden) — chosen manual list with automated updates from CA geospatial DB. |

**Translation Quality Strategy**: Pre-translate common emergency phrases (evacuation, shelter, air quality) to ensure consistency. User-submitted queries translated on-the-fly.

---

### Azure OpenAI Model Selection

| **Decision** | **Rationale** | **Alternatives Considered** |
|--------------|---------------|----------------------------|
| **GPT-4o-mini** for alert lookup and routing | Lightweight queries (alert by ZIP, shelter search, AQI check) don't need heavy reasoning. 70% cost savings vs. GPT-4o. | GPT-4o (overkill), GPT-3.5-turbo (being deprecated), text-davinci-003 (legacy) |
| **Single-agent design** (no multi-agent pipeline) | Emergency chatbot is simpler than other accelerators. One agent with deterministic tools (alert lookup, shelter search, AQI retrieval) is sufficient. | 3-agent pipeline (over-engineered for this use case) |

**Model**: `gpt-4o-mini` — fast, cost-effective, sufficient for deterministic tool calling.

---

### Azure AI Search for Emergency Knowledge Base

| **Decision** | **Rationale** | **Alternatives Considered** |
|--------------|---------------|----------------------------|
| **Azure AI Search** with metadata filters | Supports geospatial queries (ZIP code, lat/lon), metadata filtering (alert type, severity), and fast lookups (<1s) for 500+ shelters statewide. | Cosmos DB (no geospatial indexing), PostgreSQL+PostGIS (self-hosted complexity), in-memory (doesn't scale) |
| **Metadata filters**: `alert_type`, `severity`, `affected_zip_codes`, `is_active` | Ensures only current, relevant alerts are retrieved. | No filters (returns expired alerts), complex query logic (slow) |

**Index Schema**: Emergency alerts, shelters, evacuation orders, and AQI data indexed with `text-embedding-ada-002` for semantic search. ZIP codes indexed for fast location matching.

---

### SMS Gateway Selection

| **Decision** | **Rationale** | **Alternatives Considered** |
|--------------|---------------|----------------------------|
| **Azure Communication Services SMS** | Native Azure integration, CA-compliant data residency (West US 2/3), supports inbound/outbound SMS, toll-free numbers. | Twilio (vendor lock-in, but proven), Bandwidth (less integration), no SMS (excludes low-bandwidth users) |
| **Rate limiting**: 10 SMS per phone number per hour | Prevents abuse during high-volume events (wildfires, earthquakes). Legitimate users rarely need >10 queries/hour. | No limit (spam risk), 5/hour (too restrictive for multi-question conversations) |
| **Phone number hashing** (SHA-256) | Anonymizes phone numbers in logs. Prevents PII leakage. | Plain text (CCPA violation), no SMS (reduces accessibility) |

**Implementation**: Inbound SMS webhook → FastAPI endpoint → emergency agent → outbound SMS response. Session state tracks last 10 messages per hashed phone number.

---

### Low-Bandwidth Mode Strategy

| **Decision** | **Rationale** | **Alternatives Considered** |
|--------------|---------------|----------------------------|
| **Server-side rendering (SSR) fallback** | When `?lowbandwidth=true` detected or network speed <200 Kbps, serve Jinja2-rendered HTML (no React, no JS). Page size: <50 KB. | Progressive enhancement (complex), separate mobile site (2x maintenance), no fallback (excludes rural CA) |
| **Automatic bandwidth detection** | Frontend JS measures network speed on load. If slow, switch to SSR mode. | Manual toggle only (user burden), no detection (users don't know about low-bandwidth mode) |
| **Text-only content, inline CSS** | No external stylesheets, no images, no fonts. All styles inlined in `<style>` tags. Works on 2G connections. | External CSS (fails on slow networks), minimal images (still too heavy) |

**SSR Implementation**: FastAPI serves `/emergency-low` route with Jinja2 templates. No WebSockets, no live updates — user refreshes page for new alerts.

---

## Architecture Decisions

### Single Agent vs. Multi-Agent Pipeline

| **Decision** | **Rationale** |
|--------------|---------------|
| **Single-agent design** | Emergency chatbot is simpler than other accelerators. No complex routing or escalation needed. One agent with deterministic tools (alert lookup, shelter search, AQI retrieval, evacuation check) is sufficient. |
| **Alternative rejected**: 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) | Over-engineered for this use case. Emergency queries are straightforward: "What's the air quality in 94102?" → AQI lookup tool. No ambiguity requiring multi-agent orchestration. |

**Agent Responsibility**: Single `emergency_agent.py` with `@kernel_function` tools for alert lookup, shelter search, AQI retrieval, evacuation status, and translation.

---

### Translation Architecture

| **Decision** | **Rationale** |
|--------------|---------------|
| **Server-side translation** | Backend translates both user input (target → English) and assistant response (English → target language). Frontend is language-agnostic. | Client-side translation (exposes Azure API keys), hybrid (complex), no translation (English-only) |
| **Language detection** | Azure Translator auto-detects user input language. No explicit language selection required. | Manual selection (user burden), browser locale (unreliable for multilingual users) |
| **Fallback to English** | If Azure Translator unavailable (429/503), display English-only warning and continue. | Block all queries (unusable), use Google Translate (vendor lock-in) |

**Translation Flow**:
1. User submits query in Spanish: "¿Cuál es la calidad del aire en San Francisco?"
2. Backend detects Spanish, translates to English: "What is the air quality in San Francisco?"
3. Agent processes query (English), calls AQI tool, gets result
4. Backend translates response to Spanish: "La calidad del aire es Mala (AQI: 165). Evite actividades al aire libre."
5. Frontend displays Spanish response

---

### Caching Strategy

| **Decision** | **Rationale** |
|--------------|---------------|
| **Translation cache** (Redis, 24-hour TTL) | Emergency alerts rarely change within 24 hours. Cache key: `{content_hash}_{target_lang}`. Reduces Azure Translator API calls by ~60%. | No caching (expensive), shorter TTL (more API calls), longer TTL (stale translations) |
| **Alert cache** (in-memory, 5-minute TTL) | Alerts updated every 5 minutes from Cal OES feed. Cache prevents redundant Azure AI Search queries. | No caching (slow), longer TTL (stale alerts during fast-moving events) |
| **Shelter capacity cache** (in-memory, 10-minute TTL) | Shelter capacity updates less frequently than alerts. Cache reduces lookup latency. | Real-time only (high latency), no caching (expensive) |

**Cache Invalidation**: Translation cache purged on manual flush (admin endpoint). Alert cache auto-expires every 5 minutes.

---

### Synchronous vs. Asynchronous Tool Execution

| **Decision** | **Rationale** |
|--------------|---------------|
| **Synchronous tools** within LLM call | Alert lookups (<500ms), shelter searches (<800ms), AQI checks (<300ms) all fast enough for synchronous execution. No need for async complexity. | Async with polling (adds latency, complexity) |

**Implementation**: All `@kernel_function` tools execute synchronously within Semantic Kernel's `InvokeAsync()` call. Client waits for full response.

---

## Mock Mode Strategy

### Mock Data Coverage

| **Data Type** | **Mock Coverage** | **Real Data Source** |
|---------------|-------------------|---------------------|
| **Emergency Alerts** | 20+ samples (fire, flood, AQI, earthquake, tsunami) covering major CA cities | Cal OES emergency feed API |
| **Shelters** | 100+ shelters statewide (ADA, pets, medical, food services) | Red Cross, Cal OES shelter database |
| **Evacuation Orders** | 10+ zones (mandatory, voluntary) with road closures | County emergency management systems |
| **AQI Data** | 50+ monitoring stations (PurpleAir, AirNow) with PM2.5, PM10, ozone | EPA AirNow API, PurpleAir API |
| **Translations** | English ↔ Spanish, Chinese, Vietnamese (3 languages) | Azure Translator (70+ languages in real mode) |

**Mock Implementation**:
```python
# backend/app/services/alert_service.py
if os.getenv("USE_MOCK_SERVICES") == "true":
    return load_mock_alerts(zip_code)
else:
    return fetch_from_cal_oes_api(zip_code)
```

---

### Translation Mock Strategy

| **Decision** | **Rationale** |
|--------------|---------------|
| **3 languages in mock mode** (English, Spanish, Chinese) | Covers 80% of CA non-English speakers. Reduces mock data size. | 70+ languages (too large for mock JSON), English-only (doesn't test translation logic) |
| **Canned translations** for common phrases | "Evacuation order", "Air quality", "Shelter" pre-translated. User queries translated via simple pattern matching. | Real Azure Translator in mock (requires credentials), no translation (doesn't test flow) |

**Mock Translation Example**:
```json
{
  "en": "Wildfire warning in your area. Prepare for possible evacuation.",
  "es": "Advertencia de incendio forestal en su área. Prepárese para una posible evacuación.",
  "zh-Hans": "您所在地区有野火警告。准备可能的疏散。"
}
```

---

## Risk Analysis

### Risk 1: Translation Quality for Emergency Instructions

**Severity**: High (mistranslation could endanger lives)

**Scenario**: Azure Translator mistranslates "mandatory evacuation" as "voluntary evacuation" in Vietnamese. Residents don't evacuate.

**Mitigation**:
1. **Pre-translate critical phrases** (evacuation, shelter, danger, safe) with human review (Cal OES multilingual staff)
2. **Proper noun exclusion list** prevents translating location names (e.g., "Los Angeles" stays "Los Angeles")
3. **Fallback to English** if translation confidence <0.8 (Azure Translator returns confidence scores)
4. **User feedback mechanism**: "Was this translation helpful? [Yes] [No]" → flags low-quality translations for review

**Residual Risk**: Medium (Azure Translator generally high-quality, but edge cases possible for less common languages like Hmong, Punjabi)

---

### Risk 2: Stale Alert Data During Fast-Moving Events

**Severity**: High (outdated evacuation orders could endanger lives)

**Scenario**: Wildfire spreads rapidly. Evacuation order expands from Zone A to Zone B. Alert cache still shows Zone A only (5-minute TTL not expired).

**Mitigation**:
1. **Short cache TTL** (5 minutes for alerts, 1 minute for evacuation orders)
2. **Manual cache flush endpoint** for emergency managers: `POST /admin/flush-cache` (authenticated)
3. **Last-updated timestamp** on every alert: "As of 2:35 PM" — users know data freshness
4. **Real-time fallback**: If alert age >5 minutes, bypass cache and fetch live data

**Residual Risk**: Medium (5-minute lag acceptable for most emergencies; manual flush available for critical updates)

---

### Risk 3: SMS Abuse During Major Events

**Severity**: Medium (SMS gateway overload, legitimate users can't get help)

**Scenario**: Earthquake hits LA. 100k residents text the chatbot simultaneously. SMS gateway rate limits kick in, legitimate users get errors.

**Mitigation**:
1. **Rate limiting**: 10 SMS per phone number per hour (prevents spam)
2. **Auto-scaling**: Azure Communication Services SMS scales to 10k messages/second
3. **Priority queuing**: If >1000 SMS/minute, prioritize new conversations over follow-ups
4. **Fallback message**: "High volume right now. For urgent help, call 911. For shelter info, visit emergency.ca.gov."

**Residual Risk**: Low (rate limiting prevents abuse; auto-scaling handles legitimate spikes)

---

### Risk 4: Low-Bandwidth Mode Not Discoverable

**Severity**: Low (rural users don't know about text-only mode)

**Scenario**: User in rural CA tries to load full React app on 2G connection. Page fails to load. User gives up.

**Mitigation**:
1. **Automatic detection**: Frontend JS measures network speed on load. If <200 Kbps, auto-redirect to `/emergency-low`
2. **Manual link**: Full app footer includes "Slow connection? Try text-only mode" link
3. **SMS auto-response**: First SMS to chatbot includes: "For faster responses, text LOW to switch to text-only mode"
4. **Public awareness**: Cal OES includes "Text-only mode available" in emergency preparedness materials

**Residual Risk**: Low (automatic detection catches most cases; SMS/text-only mode always available)

---

### Risk 5: Proper Noun Translation Errors

**Severity**: Medium (confusing location names)

**Scenario**: Azure Translator translates "San Francisco" to "圣弗朗西斯科" (correct Chinese), but also translates "Paradise, CA" to "天堂，加州" (literal translation of "Paradise"). User doesn't recognize their town.

**Mitigation**:
1. **Exclusion list**: 500+ CA city names, street names, shelter names excluded from translation
2. **Romanization for Chinese/Korean**: Show both translated and romanized versions: "圣弗朗西斯科 (San Francisco)"
3. **User feedback**: "Was this location clear? [Yes] [No]" → flags confusing translations
4. **Automated list updates**: Sync exclusion list with CA geospatial database monthly

**Residual Risk**: Low (exclusion list covers 95% of CA locations; romanization helps remaining 5%)

---

## Performance Considerations

### Latency Targets

| **Operation** | **Target** | **Current Estimate** | **Bottleneck** |
|---------------|-----------|---------------------|----------------|
| Alert lookup | <3s | 1-2s | Azure AI Search query + translation |
| Shelter search | <2s | 1.5s | Geospatial query + capacity check |
| AQI retrieval | <2s | 0.5-1s | API call to AirNow + translation |
| Evacuation status | <3s | 2s | Geospatial match + road closures |
| SMS response | <10s | 5-8s | Translation + agent processing + SMS send |

**Optimization Strategy**:
- **Parallelize translation and tool calls**: If user query needs translation AND tool execution, do both simultaneously
- **Geospatial indexing**: Pre-index all shelters/alerts by ZIP code for O(1) lookup
- **Streaming responses**: Return alert summary first, then details (SSE)

---

### Scaling Approach

| **Component** | **Scaling Strategy** | **Justification** |
|---------------|---------------------|-------------------|
| **Backend API** | Horizontal (Azure Container Apps autoscale) | Stateless FastAPI — scales linearly with concurrent users |
| **Translation caching** | Redis with 24-hour TTL | Reduces Azure Translator API calls by 60% (cache hit rate target) |
| **Azure AI Search** | Standard tier (50 RPS) | 10k users = ~300 QPS peak → Standard tier sufficient with caching |
| **SMS gateway** | Azure Communication Services autoscale | Handles 10k messages/second (far exceeds expected load) |

**Cost Model**: 10k daily users × 2 queries avg = 20k queries/day × $0.01/query (GPT-4o-mini + search + translation) = ~$200/day = $6k/month.

---

### Translation Caching Impact

| **Metric** | **Without Cache** | **With Cache (60% hit rate)** | **Savings** |
|------------|-------------------|------------------------------|-------------|
| **Azure Translator API calls** | 20k/day | 8k/day | 60% reduction |
| **Translation cost** | $200/day ($0.01/call) | $80/day | $120/day = $3.6k/month |
| **Latency (avg)** | 1.2s | 0.6s | 50% faster |

**Cache Implementation**: Redis (production), in-memory dict (dev). Cache key: `{MD5(content)}_{target_lang}`. TTL: 24 hours.

---

## Security Considerations

### PII Handling

| **PII Type** | **Storage** | **Transmission** | **Logging** |
|--------------|-------------|------------------|-------------|
| **Phone Number (SMS)** | SHA-256 hash only | N/A (inbound SMS) | Hash only, raw number never logged |
| **User Location (ZIP, address)** | Not stored (query-only) | HTTPS only | Redacted in logs (replace with "REDACTED_ZIP") |
| **SMS Conversation** | Stored for 7 days (debugging), then deleted | HTTPS | No PII (phone hash, message content only) |

**Encryption**:
- **At rest**: Azure SQL TDE (Transparent Data Encryption)
- **In transit**: TLS 1.3 for all API calls

---

### Compliance Requirements

| **Regulation** | **Requirement** | **Implementation** |
|----------------|----------------|-------------------|
| **EO N-12-23** | No training on CA resident data | Azure OpenAI Data Processing Addendum (no training) |
| **CCPA/CPRA** | User data deletion on request | `/emergency/delete-my-data` endpoint deletes all SMS session data for hashed phone number |
| **Cal OES Privacy Policy** | No sharing with 3rd parties | All data stays within Azure (CA-compliant regions: West US 2, West US 3) |

**Data Retention**:
- **SMS conversations**: 7 days (debugging only)
- **Translation cache**: 24 hours (auto-expires)
- **Alert lookups**: Not stored (query-only)

---

### Authentication and Authorization

| **Endpoint** | **Auth Required** | **Mechanism** |
|--------------|-------------------|---------------|
| `POST /emergency/alerts` | No (public) | None (rate-limited by IP) |
| `POST /emergency/shelters` | No (public) | None (rate-limited by IP) |
| `POST /emergency/aqi` | No (public) | None (rate-limited by IP) |
| `POST /sms/inbound` | Yes (webhook signature) | Azure Communication Services signature validation |
| `POST /admin/flush-cache` | Yes (admin only) | Azure AD OAuth 2.0 (Cal OES staff) |

**Rate Limiting**:
- **Web**: 30 requests/minute per IP
- **SMS**: 10 messages/hour per phone number
- **Admin**: Unlimited (authenticated Cal OES staff)

---

## Mock Strategy Implementation

### Mock Data Structure

**Location**: `backend/mocks/`

```
emergency_alerts.json   # 20+ alerts (fire, flood, AQI, earthquake)
shelters.json           # 100+ shelters statewide
evacuation_orders.json  # 10+ zones (mandatory, voluntary)
air_quality.json        # 50+ AQI monitoring stations
translations.json       # Common phrases in 3 languages
```

**Mock Services**:

```python
# backend/app/services/alert_service.py
class AlertService:
    def __init__(self):
        self.use_mock = os.getenv("USE_MOCK_SERVICES") == "true"
        if self.use_mock:
            with open("backend/mocks/emergency_alerts.json") as f:
                self.mock_alerts = json.load(f)
    
    async def get_alerts_by_zip(self, zip_code: str) -> List[EmergencyAlert]:
        if self.use_mock:
            return self._get_mock_alerts(zip_code)
        else:
            return await self._fetch_from_cal_oes_api(zip_code)
```

---

### Mock vs. Real Behavior Parity

| **Feature** | **Mock Behavior** | **Real Behavior** | **Parity Level** |
|-------------|-------------------|-------------------|------------------|
| **Alert lookup** | JSON file lookup by ZIP | Azure AI Search semantic query | 90% (same response schema) |
| **Shelter search** | Keyword + distance calc in JSON | Azure AI Search geospatial query | 85% (mock lacks geospatial ranking) |
| **AQI retrieval** | JSON file lookup by location | EPA AirNow API | 95% (same data schema) |
| **Translation** | 3 languages (canned phrases) | Azure Translator (70+ languages) | 60% (mock simpler, limited languages) |
| **SMS** | Simulated inbound/outbound | Azure Communication Services | 80% (mock doesn't test webhook signature) |

**Testing Strategy**: E2E tests run against mock mode. Smoke tests verify real mode endpoints (requires Azure credentials, CI/CD only).

---

## References

- **Azure Translator**: [Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/translator/)
- **Azure Communication Services SMS**: [Quickstart](https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/sms/send)
- **Cal OES Emergency Alerts**: [Cal OES Public API](https://www.caloes.ca.gov/)
- **EPA AirNow API**: [AirNow Developer Guide](https://docs.airnowapi.org/)
- **WCAG AA Compliance**: [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
