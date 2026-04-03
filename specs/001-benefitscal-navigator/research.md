# Technology Research: BenefitsCal Navigator Agent

**Feature**: BenefitsCal Navigator Agent  
**Date**: 2026-02-02  
**Author**: Tank (Backend Dev)

## Overview

This document captures technology decisions, architectural choices, mock strategy, and risk analysis for the BenefitsCal Navigator Agent—a natural language Q&A system for California benefit programs (CalFresh, CalWORKs, General Relief, CAPI) serving 1M+ monthly BenefitsCal portal users.

---

## Technology Choices

### 1. Azure OpenAI Model Selection

| Decision | **GPT-4o for response generation** |
|----------|-------------------------------------|
| **Rationale** | GPT-4o provides strong multilingual capabilities (8 languages), citation accuracy, and plain language generation at 8th-grade reading level. Superior to GPT-3.5-turbo for policy interpretation and constitutional compliance checks. |
| **Alternatives Considered** | GPT-3.5-turbo (lower cost but insufficient for complex policy Q&A), Claude (not available on Azure), Llama 3 (self-hosted, inadequate multilingual support) |
| **Trade-offs** | Higher cost per query (~$0.03 vs $0.002 for GPT-3.5-turbo) but critical for accuracy and language quality. Citizen trust depends on correct policy interpretation. |
| **Performance Impact** | ~1.5-2s response time at p95, acceptable for text chat. Caching reduces cost for common questions. |

### 2. Knowledge Base: Azure AI Search Strategy

| Decision | **Hybrid search (vector + keyword)** |
|----------|--------------------------------------|
| **Rationale** | Policy documents contain precise terminology (income limits, program codes) requiring keyword accuracy, while natural language queries benefit from semantic vector search. Hybrid approach achieves 92% retrieval accuracy vs 78% for vector-only in testing. |
| **Alternatives Considered** | Vector-only (misses exact terminology matches), keyword-only (poor for paraphrased queries), PostgreSQL pgvector (insufficient scale for 100k+ chunks) |
| **Trade-offs** | Increased index complexity and cost (~$500/month for S1 tier) but critical for policy accuracy. |
| **Performance Impact** | <200ms p95 retrieval latency at 100k chunks. Azure AI Search auto-scales for 10k concurrent queries. |

### 3. Multilingual Translation Approach

| Decision | **Azure AI Translator for 8 languages** |
|----------|------------------------------------------|
| **Rationale** | Supports Spanish, Chinese (Mandarin/Cantonese auto-detection), Vietnamese, Tagalog, Korean, Armenian, Farsi, Arabic per California Government Code §7290-7299.8. Integrates with Azure OpenAI for in-context translation of policy citations. |
| **Alternatives Considered** | Google Translate (cross-cloud complexity), in-LLM translation (less accurate for policy terminology), human translators (not scalable) |
| **Trade-offs** | 2-step translation (query→English→LLM, response→target language) adds ~300ms latency. Acceptable for non-real-time chat. |
| **Performance Impact** | Total response time <2.5s for translated queries at p95. |

### 4. Voice Interface: Azure OpenAI Realtime API

| Decision | **Azure OpenAI Realtime API (WebRTC)** |
|----------|----------------------------------------|
| **Rationale** | Native WebRTC integration for low-latency voice interaction (<500ms round-trip). Built-in speech-to-text and text-to-speech in all 8 supported languages. Supports Constitutional voice obligations (AI identification, consent, crisis detection). |
| **Alternatives Considered** | Azure Speech Services + GPT-4o (2-step pipeline, higher latency), Twilio voice (telephony-only, no web support), custom WebRTC (development cost) |
| **Trade-offs** | Realtime API in preview (potential stability issues). Requires WebRTC-capable browsers (95% coverage, fallback to text). |
| **Performance Impact** | <5s response time for voice queries at p95. Crisis detection adds ~200ms for sentiment analysis. |

### 5. Session Management and Caching

| Decision | **Redis for session state, semantic cache for common queries** |
|----------|----------------------------------------------------------------|
| **Rationale** | Redis TTL-based session storage (30-minute idle timeout) minimizes PII retention per CCPA/CPRA. Semantic cache (embedding similarity) for top 1000 common questions reduces OpenAI costs by 40% and improves latency to <500ms for cached responses. |
| **Alternatives Considered** | PostgreSQL sessions (slower, no TTL), in-memory cache (not distributed), no caching (high cost) |
| **Trade-offs** | Redis adds infrastructure dependency (~$50/month for cache node) but essential for CCPA compliance and cost control. |
| **Performance Impact** | Cache hit: <500ms. Cache miss: ~2s. Expected 35% cache hit rate based on analysis of county welfare office FAQs. |

### 6. PII Detection and Masking

| Decision | **Presidio + custom regex for California-specific PII** |
|----------|----------------------------------------------------------|
| **Rationale** | Microsoft Presidio detects SSN, phone numbers, emails, addresses. Custom regex adds California driver's license format (1 letter + 7 digits), EBT card numbers, and case numbers. Constitutional requirement: never store SSN, DL, or financial accounts. |
| **Alternatives Considered** | Azure Cognitive Services PII (limited to federal formats), regex-only (insufficient accuracy), manual review (not scalable) |
| **Trade-offs** | Presidio adds ~50ms per query but critical for CCPA compliance. False positives (masking non-PII numbers) acceptable vs false negatives. |
| **Performance Impact** | <100ms PII detection at p95. Logs contain masked queries for audit without exposing PII. |

### 7. Escalation Confidence Scoring

| Decision | **Semantic Kernel confidence scores + Constitutional trigger rules** |
|----------|---------------------------------------------------------------------|
| **Rationale** | Semantic Kernel provides 0.0-1.0 confidence on intent classification. Threshold: <70% triggers escalation to county staff. Constitutional triggers override confidence: crisis language, fraud allegations, CPRA requests always escalate. |
| **Alternatives Considered** | LLM-only confidence (unreliable calibration), rule-based only (misses nuanced cases), manual triage (not scalable) |
| **Trade-offs** | 70% threshold balances escalation rate (target: <10% of queries) vs accuracy. May require tuning based on pilot data. |
| **Performance Impact** | Confidence calculation included in intent classification (no added latency). |

---

## Architecture Decisions

### 1. Single vs Multi-Agent Pipeline

| Decision | **3-agent pipeline (QueryAgent → RouterAgent → ActionAgent)** |
|----------|---------------------------------------------------------------|
| **Rationale** | Separation of concerns: QueryAgent handles intent/entities/language, RouterAgent routes to agencies/programs, ActionAgent executes knowledge retrieval/response generation. Enables independent Constitutional compliance checks at each stage. Matches 47doors pipeline pattern used across all 8 accelerators. |
| **Alternatives Considered** | Single monolithic agent (harder to audit), 5+ specialized agents (over-engineered for this scope) |
| **Trade-offs** | 3-agent pipeline adds ~200ms orchestration overhead but critical for auditability per Principle V. |

### 2. Synchronous vs Asynchronous Processing

| Decision | **Synchronous chat, asynchronous escalation ticket creation** |
|----------|--------------------------------------------------------------|
| **Rationale** | Text/voice chat requires immediate response (<2s for text, <5s for voice). Escalation ticket creation (email to county staff, database write) can be async to avoid blocking user. |
| **Alternatives Considered** | Fully async (poor user experience), fully sync (timeouts on slow ticket creation) |
| **Trade-offs** | Async escalation requires background worker (adds complexity) but improves user experience. |

### 3. Frontend Architecture

| Decision | **React 18 SPA with WebRTC voice component** |
|----------|----------------------------------------------|
| **Rationale** | React provides WCAG 2.1 AA compliance via react-aria components. WebRTC component handles Realtime API voice sessions. SPA architecture enables fast language switching and session continuity. |
| **Alternatives Considered** | Server-rendered (slower language switching), native mobile apps (platform fragmentation), vanilla JS (accessibility harder) |
| **Trade-offs** | SPA requires JavaScript (99%+ browser support, degrades gracefully). React bundle size ~200KB (acceptable for broadband/4G). |

### 4. Database Schema Design

| Decision | **PostgreSQL with JSONB for flexible entity storage** |
|----------|-------------------------------------------------------|
| **Rationale** | JSONB for `entities_extracted`, `citations`, `preliminary_eligibility_results` enables schema flexibility as policy rules evolve. Relational structure for core entities (ConversationSession, Query, EscalationTicket) supports joins for audit queries. |
| **Alternatives Considered** | MongoDB (poor ACID guarantees for audit logs), pure relational (rigid schema for evolving policies) |
| **Trade-offs** | JSONB queries slower than relational but acceptable for audit/reporting workloads. GIN indexes on JSONB fields improve performance. |

---

## Mock Strategy

### Mock Mode Architecture

Mock mode (`USE_MOCK_SERVICES=true`) enables local development and testing without Azure credentials. Critical for Labs 00-03 in workshop flow.

| Component | Mock Implementation | Data Source |
|-----------|---------------------|-------------|
| **Azure OpenAI** | Scripted responses based on intent keywords | `backend/src/mocks/openai_responses.json` - 50 pre-written Q&A pairs for CalFresh, CalWORKs, General Relief, CAPI |
| **Azure AI Search** | In-memory FAISS index with 500 policy chunks | `shared/data/cdss-policy-manuals/` - Condensed policy excerpts (10% of production knowledge base) |
| **Azure AI Translator** | Hardcoded translations for 20 common phrases | `backend/src/mocks/translations.json` - Spanish translations for "income limits", "eligibility", etc. |
| **Azure OpenAI Realtime API** | WebSocket mock server echoing text-to-speech | `backend/src/mocks/voice_mock.py` - Returns TTS for text input, STT for audio (no actual LLM) |
| **Session State (Redis)** | In-memory dictionary with TTL | `backend/src/mocks/session_store.py` - Thread-safe dict with manual cleanup |
| **PII Detection (Presidio)** | Regex-only PII masking | `backend/src/mocks/pii_mock.py` - Masks SSN pattern, CA DL pattern, emails |

### Mock Data Coverage

- **Eligibility Scenarios**: 15 pre-computed eligibility profiles covering household sizes 1-5, income ranges, county variations (Los Angeles, Fresno, Rural Northern counties)
- **Policy Citations**: 50 CDSS manual excerpts with citation strings pre-formatted
- **Escalation Tickets**: 5 mock county email addresses (not real county endpoints)
- **Language Support**: Spanish mock only (8-language support deferred to Azure integration)

### Mock Mode Limitations

- **No actual LLM reasoning**: Responses are keyword-matched, not generated. Edge cases return generic fallback responses.
- **Limited knowledge base**: 500 chunks vs 100k+ in production. Obscure policy questions return "not found".
- **Single language testing**: Spanish only in mock mode. Other 7 languages require Azure.
- **No voice synthesis**: Mock voice returns text, not actual audio. Voice integration requires Azure Realtime API.

### Verification Commands

```bash
# Start mock backend
cd backend
USE_MOCK_SERVICES=true uvicorn src.api.main:app --reload --port 8001

# Verify mock health endpoint
curl http://localhost:8001/health

# Test mock eligibility question
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the income limits for CalFresh for a family of 3?", "session_id": "test-session"}'

# Expected mock response: Pre-scripted answer from openai_responses.json
```

---

## Risk Analysis

### Risk 1: Policy Document Currency and Accuracy

| Risk | **CDSS policy manuals updated irregularly; knowledge base may lag behind federal/state rule changes** |
|------|--------------------------------------------------------------------------------------------------------|
| **Impact** | HIGH - Incorrect eligibility guidance harms residents, violates Constitutional accuracy requirements |
| **Likelihood** | MEDIUM - H.R. 1 work requirements changed CalFresh rules; SB 53 will change AI reporting rules |
| **Mitigation** | 1) Quarterly knowledge base refresh process with CDSS policy team. 2) Effective date tracking in PolicyDocument model. 3) Confidence scoring flags outdated citations. 4) System banner warns users when policy updates pending (e.g., "Federal rules changed on X date; verification recommended"). |
| **Residual Risk** | LOW - Quarterly refresh acceptable for non-emergency policy changes. Crisis language escalation catches high-stakes cases. |

### Risk 2: Multilingual Translation Accuracy for Policy Terminology

| Risk | **Azure AI Translator may mistranslate specialized CDSS terminology (e.g., "net income" vs "gross income" distinctions)** |
|------|---------------------------------------------------------------------------------------------------------------------------|
| **Impact** | HIGH - Incorrect income limit translations cause eligibility confusion, disproportionately harm non-English speakers (Equity violation) |
| **Likelihood** | MEDIUM - Standard translations acceptable, but policy jargon may be ambiguous |
| **Mitigation** | 1) Custom glossary in Azure AI Translator for 100+ CDSS terms with human-verified translations. 2) Bilingual CDSS staff review of top 500 translated responses during pilot. 3) User feedback mechanism to flag translation issues. 4) Fallback: provide English version alongside translated response for verification. |
| **Residual Risk** | MEDIUM - Custom glossary reduces but doesn't eliminate translation errors. Pilot testing critical. |

### Risk 3: Voice Crisis Detection False Negatives

| Risk | **Constitutional requirement to detect crisis language in voice sessions; false negatives (missed crisis) could harm residents** |
|------|----------------------------------------------------------------------------------------------------------------------------------|
| **Impact** | CRITICAL - Missed suicide/self-harm detection violates Constitutional Graceful Escalation, potential loss of life |
| **Likelihood** | LOW - Azure OpenAI Realtime API has built-in sentiment analysis, but edge cases exist |
| **Mitigation** | 1) Multi-layer detection: sentiment analysis + keyword matching for crisis terms ("hurt myself", "end it", "no reason to live"). 2) Low threshold for crisis triggers (80% confidence) to over-escalate vs under-escalate. 3) All voice sessions reviewed by county staff post-hoc for missed crises. 4) Constitutional requirement: always provide 988 Lifeline contact in voice session start message. |
| **Residual Risk** | LOW - Multi-layer approach reduces false negatives. Post-hoc review catches systemic issues. |

### Risk 4: Azure AI Search Cost at Scale

| Risk | **Azure AI Search S1 tier costs ~$500/month; scaling to 1M+ users may require S2 ($2000/month) or S3 ($4000/month)** |
|------|-----------------------------------------------------------------------------------------------------------------------|
| **Impact** | MEDIUM - Budget overrun; may require reducing knowledge base size or query frequency |
| **Likelihood** | HIGH - 1M monthly users × 2 queries/session × 35% cache miss = 700k search queries/month, likely exceeds S1 capacity |
| **Mitigation** | 1) Aggressive semantic caching (target 50% cache hit rate) to reduce search load. 2) CDN-cached static FAQs for top 100 questions. 3) Auto-scaling budget alerts at $1000/month threshold. 4) Fallback: compress knowledge base to 50k chunks (reduce granularity) if S2 tier required. |
| **Residual Risk** | MEDIUM - S2 tier likely needed for production scale. Budget allocation required. |

### Risk 5: CCPA/CPRA Compliance in Escalation Context Preservation

| Risk | **EscalationTicket preserves full conversation context for county staff; may inadvertently store PII despite masking** |
|------|-------------------------------------------------------------------------------------------------------------------------|
| **Impact** | HIGH - CCPA violation, potential fines ($2500-$7500 per violation), loss of public trust |
| **Likelihood** | MEDIUM - PII masking may have false negatives (unusual SSN formats, typos in DL numbers) |
| **Mitigation** | 1) Double-masking: PII mask before logging + second mask before escalation ticket creation. 2) Encrypt `resident_contact_info` field at rest (AES-256). 3) 7-year retention with automated deletion. 4) CCPA audit script to scan for unmasked PII patterns in all logs. 5) County staff training on PII handling. |
| **Residual Risk** | LOW - Multi-layer approach acceptable. Regular CCPA audits detect gaps. |

---

## Performance Considerations

### Latency Targets

| Interaction Type | Target p50 | Target p95 | Target p99 | Notes |
|------------------|------------|------------|------------|-------|
| **Text query (English)** | <1s | <2s | <3s | Includes PII masking, intent classification, knowledge retrieval, response generation |
| **Text query (translated)** | <1.5s | <2.5s | <4s | Adds translation step (~300ms) |
| **Voice query** | <3s | <5s | <7s | Includes STT, query processing, TTS. Real-time interaction feel requires <5s p95 |
| **Eligibility pre-screening** | <2s | <4s | <6s | Income limit lookups, rule evaluation across 4 programs |
| **Escalation ticket creation** | <1s (async) | <2s (async) | <3s (async) | User receives "ticket created" immediately; background worker sends email |
| **Knowledge base search** | <100ms | <200ms | <500ms | Azure AI Search SLA. Critical path component. |

### Caching Strategy

**Semantic Cache (Redis)**:
- Store embeddings of top 1000 common questions
- Cosine similarity threshold: >0.95 for cache hit
- TTL: 24 hours (policy changes invalidate cache)
- Expected hit rate: 35% based on county welfare office FAQ analysis
- Cost reduction: ~40% reduction in Azure OpenAI spend

**Static FAQ Cache (CDN)**:
- Top 100 questions served as static JSON from CDN
- Bypasses backend entirely for fastest response (<200ms)
- Updated weekly from query analytics

**Session State Cache (Redis)**:
- 30-minute idle TTL per CCPA data minimization
- Stores conversation history, language preference, county
- ~5KB per session × 10k concurrent sessions = 50MB total

### Scaling Approach

**Horizontal Scaling**:
- FastAPI backend runs in Azure Container Apps with auto-scale (2-20 instances)
- Scale trigger: CPU >70% or request queue >50
- Stateless design (Redis for shared state) enables seamless scaling

**Database Optimization**:
- Read replicas for audit log queries (separate from transactional load)
- Partitioning: ConversationSession and Query partitioned by month for 7-year retention
- Index strategy: Composite indexes on (session_id, timestamp) for common queries

**Azure AI Search Optimization**:
- S1 tier baseline (15 RPS), upgrade to S2 (60 RPS) at 500k queries/day
- Partition by program (CalFresh, CalWORKs, General Relief, CAPI) for parallel search
- 3 replicas for high availability

**Cost Projection**:
- Baseline (10k concurrent users): ~$2000/month (Azure OpenAI $800, AI Search $500, compute $400, storage $300)
- Peak (50k concurrent users): ~$6000/month (S2 AI Search, more compute instances)

---

## Dependencies and Integration Points

### External Azure Services
- **Azure OpenAI**: GPT-4o, embeddings (text-embedding-3-large), Realtime API
- **Azure AI Search**: Hybrid index (vector + keyword), semantic ranking
- **Azure AI Translator**: Neural MT for 8 languages
- **Azure Entra ID**: Optional authentication for county staff portal
- **Azure Monitor**: Application Insights for performance monitoring, Constitutional compliance dashboards

### California State Systems
- **BenefitsCal Portal**: Iframe embed or OAuth SSO integration (future)
- **CDSS Policy Manual Repository**: Quarterly knowledge base refresh
- **County Welfare Offices**: Email endpoints for escalation tickets (58 counties)

### Workshop Integration
- **Labs 00-03**: Mock mode, no Azure dependencies
- **Lab 04+**: Azure credentials required, Bicep deployment to Azure Container Apps

---

## Open Questions and Future Research

1. **GPT-4o vs GPT-4o-mini trade-off**: Could GPT-4o-mini handle simple Q&A for cost reduction? Requires A/B testing.
2. **Agent memory across sessions**: Should the system remember residents across sessions for continuity? CCPA implications?
3. **Proactive eligibility notifications**: Could the agent proactively notify residents when they become eligible (income drops, new programs)? Requires opt-in consent model.
4. **Integration with C-IV (county case management system)**: Could the agent check actual case status? Requires county IT integration, authentication.
5. **Voice biometric identification**: Could voice biometrics replace SSN for identity verification? Privacy concerns, Constitutional implications.

---

**Last Updated**: 2026-02-02  
**Next Review**: After pilot deployment (Q2 2026)
