# Research & Technology Decisions: EDD Claims Assistant

**Feature**: 007-edd-claims-assistant  
**Date**: 2026-04-02  
**Author**: Neo (Security Specialist)  
**Status**: Approved

This document captures the technology choices, architectural decisions, mock strategy, and risk analysis for the EDD Claims Assistant accelerator.

---

## Technology Choices

### Azure OpenAI Model Selection

| **Decision** | **Rationale** | **Alternatives Considered** |
|--------------|---------------|----------------------------|
| **GPT-4o** for claims Q&A and routing | High accuracy for policy interpretation, function calling support, strong citation generation | GPT-4o-mini (too low accuracy for policy), GPT-4-turbo (deprecated), Claude (not Azure-hosted) |
| **GPT-4o-mini** for claim status lookups | Deterministic tool calls don't need heavy reasoning; 60% cost savings | GPT-4o (overkill for simple lookups), text-davinci-003 (legacy) |
| **Azure OpenAI Realtime API** for voice | Native WebRTC transport, tool calling support in voice mode, CA-compliant Azure infrastructure | Google Dialogflow (vendor lock-in), ElevenLabs (PII compliance concerns), Deepgram+custom (high complexity) |

**Voice Model**: `gpt-4o-realtime-preview` — supports tool calls during voice sessions, enabling claim lookup and eligibility screening via spoken conversation.

---

### Azure AI Search for Policy Knowledge Base

| **Decision** | **Rationale** | **Alternatives Considered** |
|--------------|---------------|----------------------------|
| **Azure AI Search** with semantic ranking | Integrated with Azure OpenAI, supports metadata filtering (claim type, effective dates), handles 500+ policy articles efficiently | Pinecone (external dependency), Weaviate (self-hosted complexity), RAG over blob storage (no semantic ranking) |
| **Hybrid search** (vector + keyword) | Improves recall for legal terminology ("UI Code Section 1253(c)") that vector search alone may miss | Pure vector search (misses exact citations), keyword-only (poor semantic understanding) |
| **Metadata filters**: `claim_type`, `effective_date`, `is_active` | Ensures only current, relevant policies are retrieved | No filters (risk of outdated policy answers) |

**Index Schema**: Each policy article embedded with `text-embedding-ada-002`, includes `title`, `content`, `claim_types[]`, `citations[]`, `effective_date`, `expiration_date`.

---

### Identity Verification Strategy

| **Decision** | **Rationale** | **Alternatives Considered** |
|--------------|---------------|----------------------------|
| **Last 4 SSN + Date of Birth** for claim lookups | Low friction, matches EDD's existing phone verification process | ID.me (requires 3rd party account), Login.gov (CA not yet integrated), full SSN (excessive PII exposure) |
| **Rate limiting**: 5 failed attempts → 30-minute lockout | Prevents claim enumeration attacks while allowing legitimate retries | 3 attempts (too strict for typos), no lockout (security risk) |
| **SHA-256 hashing** for session phone numbers (SMS) | Anonymizes phone numbers in logs, prevents PII leakage | Plain text storage (CCPA violation), no SMS (reduces accessibility) |

**Implementation**: `IdentityVerification` model tracks attempts per session. Backend never logs SSN or DOB — only verification success/failure.

---

### PII Redaction and Compliance

| **Decision** | **Rationale** | **Alternatives Considered** |
|--------------|---------------|----------------------------|
| **Azure OpenAI Data Processing Addendum** | Ensures no training on EDD claimant data (EO N-12-23 compliance) | OpenAI public API (not CA-compliant), local LLM (insufficient accuracy) |
| **Server-side PII filtering** with regex + NER | Redacts SSN, claim numbers, DOB from logs before storage | Client-side only (unreliable), no redaction (CCPA violation) |
| **Pydantic validators** on all PII fields | Enforces hash-only storage for `claimant_id`, prevents accidental logging | Manual validation (error-prone) |

**Regex Patterns**: SSN (`\d{3}-\d{2}-\d{4}`), Claim ID (`UI-\d{4}-\d{6}`), DOB (`\d{2}/\d{2}/\d{4}`). Named Entity Recognition (NER) catches variations.

---

### Voice Implementation Architecture

| **Decision** | **Rationale** | **Alternatives Considered** |
|--------------|---------------|----------------------------|
| **Azure OpenAI Realtime API** with WebRTC | Lowest latency (<300ms round-trip), native tool calling, Azure-hosted (CA compliance) | Speech-to-Text + GPT-4o + Text-to-Speech (higher latency, complex orchestration), Twilio Voice (vendor lock-in) |
| **Shared 3-agent pipeline** (text + voice) | Reuses `QueryAgent → RouterAgent → ActionAgent` for both modalities, reduces code duplication | Separate voice agent (2x maintenance burden), voice-only simplification (loses parity) |
| **VoiceMessage → ConversationMessage** conversion | Voice transcripts appended to `ConversationSession.messages` with `modality: "voice"`, enabling modality switching mid-conversation | Separate voice sessions (loses context on switch) |

**Fallback Strategy**: If Realtime API unavailable (429/503), frontend displays "Voice temporarily unavailable. Continue with text?" and switches to text-only mode.

---

## Architecture Decisions

### Single Agent vs. Multi-Agent Pipeline

| **Decision** | **Rationale** |
|--------------|---------------|
| **3-agent pipeline** (QueryAgent → RouterAgent → ActionAgent) | Matches 47doors constitution pattern. QueryAgent detects intent (claim lookup vs. eligibility vs. Q&A), RouterAgent handles escalation triggers, ActionAgent executes tools. |
| **Alternative rejected**: Single agent with all tools | Would violate Principle II (one LLM call per turn) if escalation detection required separate reasoning step. 3-agent keeps each call focused. |

**Agent Responsibilities**:
- **QueryAgent**: Intent classification, entity extraction (claim number, claim type), PII detection
- **RouterAgent**: Escalation trigger detection ("I want a person", "appeal", sentiment analysis), priority setting
- **ActionAgent**: Tool execution (policy search, claim lookup, eligibility assessment), response formatting with citations

---

### Synchronous vs. Asynchronous Tool Execution

| **Decision** | **Rationale** |
|--------------|---------------|
| **Synchronous tools** within LLM call | Claim lookups (<500ms), policy searches (<1s), eligibility logic (<100ms) all fast enough for synchronous execution. No need for async complexity. |
| **Alternative rejected**: Async with polling | Would add latency (client polls for results), increase complexity (job queue, status tracking), violate Principle II (orchestration overhead). |

**Implementation**: All `@kernel_function` tools execute synchronously within Semantic Kernel's `InvokeAsync()` call. Client waits for full response.

---

### Mock Mode Strategy

| **Decision** | **Rationale** |
|--------------|---------------|
| **Comprehensive mock data** in JSON fixtures | Enables full UX testing without Azure credentials (Labs 00-03 requirement). Mock covers 20+ claims, 50+ policy articles, 10+ eligibility rules. |
| **`USE_MOCK_SERVICES=true`** env var | Single flag switches all services (Azure OpenAI, Azure AI Search, Realtime API) to mock mode. Production code and mock code share same interfaces. |

**Mock Coverage**:
- **Claims**: 20+ samples across UI/DI/PFL, all statuses (pending, approved, denied), edge cases (multiple claims, pending issues)
- **Policies**: 50+ KB articles covering common questions (filing, eligibility, benefits, appeals)
- **Voice**: Canned audio responses (no Realtime API calls), simulated tool invocations

**Mock Implementation**:
```python
# backend/app/services/edd_claim_service.py
if os.getenv("USE_MOCK_SERVICES") == "true":
    return load_mock_claim(claim_id)
else:
    return fetch_from_edd_api(claim_id)
```

---

## Risk Analysis

### Risk 1: PII Leakage in Voice Transcripts

**Severity**: High (CCPA/CPRA violation, EDD reputational damage)

**Scenario**: Claimant speaks SSN during voice session. Transcript is logged to Azure OpenAI or backend logs.

**Mitigation**:
1. **Real-time PII detection** in Realtime API stream (Azure Content Safety integration)
2. **Audio cue** warns claimant: "Please don't share your Social Security number over voice. I'll ask for verification through secure channels."
3. **Server-side redaction** before logging (regex + NER on transcript chunks)
4. **Audit logs** track all PII detections for compliance review

**Residual Risk**: Medium (NER false negatives possible for ambiguous patterns like "my number is 123-45-6789")

---

### Risk 2: Claim Enumeration Attacks

**Severity**: Medium (privacy breach, claim ID guessing)

**Scenario**: Attacker brute-forces claim IDs (UI-2024-000001 → UI-2024-999999) to discover valid claims without proper verification.

**Mitigation**:
1. **Rate limiting**: Max 5 failed lookups per session, 30-minute lockout
2. **Identity verification required** (last 4 SSN + DOB) before claim data returned
3. **Non-sequential claim IDs** (UUIDs recommended, not sequential integers)
4. **Monitoring**: Alert on >10 failed lookups from same IP within 1 hour

**Residual Risk**: Low (lockout prevents large-scale enumeration)

---

### Risk 3: Outdated Policy Answers

**Severity**: Medium (misinformation, claimant frustration)

**Scenario**: EDD updates eligibility policy (e.g., work hour requirements), but knowledge base not refreshed. Assistant provides outdated answer.

**Mitigation**:
1. **Effective date tagging**: All policy articles include `effective_date` and `expiration_date`
2. **Freshness warnings**: Assistant response includes "This information is current as of [date]. For latest policy, visit edd.ca.gov."
3. **Automatic staleness detection**: Azure AI Search query filters `expiration_date > today`
4. **Monthly knowledge base refresh** (EDD policy team responsibility)

**Residual Risk**: Medium (human process dependency — if EDD doesn't notify of changes, knowledge base lags)

---

### Risk 4: Voice API Latency Spikes

**Severity**: Low (user frustration, not security issue)

**Scenario**: Azure OpenAI Realtime API has latency spike (>5s round-trip). Claimant thinks session is frozen.

**Mitigation**:
1. **Timeout detection**: If no response in 5s, show "Thinking..." indicator
2. **Fallback to text**: If 3 consecutive timeouts, offer "Voice is slow right now. Switch to text?"
3. **Graceful degradation**: If Realtime API returns 429/503, disable voice button with message
4. **Monitoring**: Track p95 latency, alert if >3s sustained

**Residual Risk**: Low (UI feedback prevents confusion)

---

### Risk 5: Escalation False Negatives

**Severity**: High (claimant doesn't get human help when needed)

**Scenario**: Claimant has urgent issue (weeks without payment, eviction threat) but doesn't use escalation keywords. Assistant fails to escalate.

**Mitigation**:
1. **Sentiment analysis**: RouterAgent detects distress signals ("desperate", "can't pay rent", "haven't eaten") and auto-escalates
2. **Explicit escalation option**: Every response includes "Need to speak with a person? Click here."
3. **Low-confidence auto-escalation**: If assistant confidence <0.7 on policy question, escalate
4. **Supervisor review**: Sample 10% of sessions for missed escalation opportunities (QA process)

**Residual Risk**: Medium (sentiment analysis not 100% accurate for implicit urgency)

---

## Performance Considerations

### Latency Targets

| **Operation** | **Target** | **Current Estimate** | **Bottleneck** |
|---------------|-----------|---------------------|----------------|
| Policy Q&A | <10s | 5-7s | Azure AI Search query + GPT-4o reasoning |
| Claim status lookup | <3s | 1-2s | Mock: instant; Real: EDD API latency |
| Eligibility assessment | <8s | 6-7s | Multi-turn Q&A (3-5 questions) |
| Voice round-trip | <15s | 10-12s | Realtime API processing + tool execution |

**Optimization Strategy**:
- **Cache policy articles** client-side (FAQ pages rarely change)
- **Parallelize tools**: If claim lookup + policy search both needed, call simultaneously
- **Streaming responses**: Return policy answer incrementally (SSE) while citations load

---

### Caching Strategy

| **Cache Layer** | **Purpose** | **TTL** | **Technology** |
|-----------------|-------------|---------|----------------|
| **Policy article cache** | Reduce Azure AI Search calls for common questions | 6 hours | Redis (production), in-memory dict (dev) |
| **Claim status cache** | Avoid redundant lookups within same session | 5 minutes | In-memory (per-session) |
| **Eligibility rules cache** | Cache decision tree logic | 24 hours | Redis |

**Cache Invalidation**: Policy cache purged on knowledge base refresh (webhook from Azure AI Search index update).

---

### Scaling Approach

| **Component** | **Scaling Strategy** | **Justification** |
|---------------|---------------------|-------------------|
| **Backend API** | Horizontal (Azure Container Apps autoscale) | Stateless FastAPI — scales linearly with concurrent users |
| **Voice sessions** | WebRTC P2P (client ↔ Azure Realtime API) | No backend relay needed; backend only receives tool calls |
| **Azure OpenAI** | Quota increase (TPM scaling) | Current quota: 100k TPM. Need 300k TPM for 10k daily users. |
| **Azure AI Search** | Standard tier (50 RPS) | 10k users = ~500 QPS peak → need Premium tier (200 RPS) or caching |

**Cost Model**: 10k daily users × 3 queries avg = 30k queries/day × $0.03/query (GPT-4o + search) = ~$900/day = $27k/month.

---

## Security Considerations

### PII Handling

| **PII Type** | **Storage** | **Transmission** | **Logging** |
|--------------|-------------|------------------|-------------|
| **SSN** | Never stored (only last 4 for verification) | HTTPS only, never in query params | Redacted before logging |
| **Claim ID** | Stored in encrypted DB (hashed claimant_id reference) | HTTPS only | Redacted in logs |
| **Date of Birth** | Never stored | HTTPS only, never in query params | Redacted before logging |
| **Phone Number (SMS)** | SHA-256 hash only | N/A (inbound SMS) | Hash only, raw number never logged |
| **Conversation Transcript** | Stored for 90 days (compliance), then deleted | HTTPS + WSS (voice) | PII-redacted version logged |

**Encryption**:
- **At rest**: Azure SQL TDE (Transparent Data Encryption)
- **In transit**: TLS 1.3 for all API calls, DTLS for WebRTC voice

---

### Compliance Requirements

| **Regulation** | **Requirement** | **Implementation** |
|----------------|----------------|-------------------|
| **EO N-12-23** | No training on CA resident data | Azure OpenAI Data Processing Addendum (no training) |
| **CCPA/CPRA** | User data deletion on request | `/edd/delete-my-data` endpoint deletes all session, transcript, claim lookup logs for claimant ID |
| **EDD Privacy Policy** | No sharing with 3rd parties | All data stays within Azure (CA-compliant regions: West US 2, West US 3) |
| **SB 53** | AI impact assessment | Documented in this file — risk: PII leakage (mitigated), bias in eligibility (N/A — rule-based) |

**Data Retention**:
- **Conversation transcripts**: 90 days (EDD audit requirement)
- **Claim lookups**: 7 days (debugging only)
- **Escalation tickets**: 1 year (case resolution tracking)

---

### Authentication and Authorization

| **Endpoint** | **Auth Required** | **Mechanism** |
|--------------|-------------------|---------------|
| `POST /edd/chat` | No (public Q&A) | None (rate-limited by IP) |
| `POST /edd/claim-status` | Yes (identity verification) | Last 4 SSN + DOB in request body, verified against claim record |
| `POST /edd/voice/session` | No (public voice Q&A) | None (rate-limited) |
| `GET /edd/claim-status/:claim_id` | Yes | Same as POST /claim-status |
| `POST /edd/delete-my-data` | Yes | Claimant ID + verification |

**Rate Limiting**:
- **Chat**: 30 requests/minute per IP
- **Claim status**: 5 requests/minute per IP (prevents brute force)
- **Voice**: 10 sessions/hour per IP (WebRTC resource limit)

---

## Mock Strategy Implementation

### Mock Data Structure

**Location**: `backend/mocks/`

```
edd_claims.json        # 20+ sample claims (UI/DI/PFL, all statuses)
edd_policies.json      # 50+ policy articles (filing, eligibility, benefits)
edd_eligibility_rules.json  # Decision tree rules for pre-screening
```

**Mock Services**:

```python
# backend/app/services/edd_claim_service.py
class EDDClaimService:
    def __init__(self):
        self.use_mock = os.getenv("USE_MOCK_SERVICES") == "true"
        if self.use_mock:
            with open("backend/mocks/edd_claims.json") as f:
                self.mock_claims = json.load(f)
    
    async def get_claim_status(self, claim_id: str) -> Claim:
        if self.use_mock:
            return self._get_mock_claim(claim_id)
        else:
            return await self._fetch_from_edd_api(claim_id)
```

**Voice Mock**: Simulated Realtime API responses (canned audio, tool call mocks):

```typescript
// frontend/src/services/voiceMockService.ts
export class VoiceMockService {
  async simulateVoiceQuery(transcript: string): Promise<VoiceResponse> {
    // Pattern match common queries
    if (transcript.includes("claim status")) {
      return {
        text: "Your claim UI-2024-123456 is approved. Next payment: April 10.",
        audio: base64EncodedCannedAudio
      };
    }
    // ... more patterns
  }
}
```

---

### Mock vs. Real Behavior Parity

| **Feature** | **Mock Behavior** | **Real Behavior** | **Parity Level** |
|-------------|-------------------|-------------------|------------------|
| **Policy Q&A** | Keyword search in `edd_policies.json` | Azure AI Search semantic query | 80% (mock lacks semantic ranking) |
| **Claim lookup** | JSON file lookup by claim ID | REST API to EDD system | 95% (same response schema) |
| **Eligibility screening** | Rule-based decision tree in JSON | Same (no external API) | 100% |
| **Voice interaction** | Canned audio responses | Azure Realtime API | 60% (no real STT/TTS, tool calls mocked) |
| **Escalation detection** | Keyword matching | Sentiment analysis (Azure AI Language) | 70% (mock simpler) |

**Testing Strategy**: E2E tests run against mock mode. Smoke tests verify real mode endpoints (requires Azure credentials, CI/CD only).

---

## References

- **EO N-12-23**: [California GenAI Guidelines](https://www.gov.ca.gov/wp-content/uploads/2023/09/AI-EO-No.12-_-GGN-Signed.pdf)
- **Azure OpenAI Realtime API**: [Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/realtime)
- **Azure AI Search Hybrid Search**: [Best Practices](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)
- **EDD Claims System**: Internal API documentation (not public)
- **CCPA/CPRA Compliance**: [CA Attorney General Guide](https://oag.ca.gov/privacy/ccpa)
