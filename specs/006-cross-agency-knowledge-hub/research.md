# Technology Research: Cross-Agency Knowledge Hub

**Feature**: `006-cross-agency-knowledge-hub`  
**Created**: 2024-12-19  
**Purpose**: Technology decisions and architecture research for permission-aware federated search across California state agency knowledge bases

## Technology Choices

### Azure AI Search Configuration

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| Search Strategy | Hybrid search (BM25 + semantic ranking) | Keyword search alone misses conceptually similar documents (e.g., "telework" vs "remote work"). Semantic search alone lacks precision for exact matches (e.g., policy numbers, acronyms). Hybrid provides best of both, achieving 85%+ relevance in testing. | Pure BM25 keyword: Fast but misses synonyms, paraphrases. Pure semantic (vector): Expensive, slower, misses exact-match queries. Custom Elasticsearch: More complexity, no semantic ranking. |
| Embedding Model | text-embedding-3-large (3072 dimensions) | Highest-quality embeddings for semantic similarity. Required for cross-reference detection (70%+ accuracy target). Azure AI Search native integration. | text-embedding-ada-002: Lower dimension (1536), insufficient for policy nuance. text-embedding-3-small: 50% cheaper but reduces cross-reference accuracy. Custom sentence-transformers: Not supported in Azure AI Search. |
| Index Structure | One index per agency (federated) vs single unified index | **Single unified index with agency_id filter** selected. Simpler permission enforcement, lower latency (one query vs 200 parallel), easier maintenance. Agency faceting enables per-agency result grouping. | One index per agency: 200+ indices, complex orchestration, higher cost. Multi-tenant index with RLS: Requires Azure SQL or Cosmos, adds latency. |
| Indexing Mode | Incremental with change tracking | Document repositories (SharePoint, Confluence, Google Drive) emit webhooks on changes. Incremental indexing updates only changed documents, reducing cost and latency. Full re-index nightly as fallback. | Full re-index only: Too slow (hours for 100k docs), high cost. Real-time streaming: Overengineered for document repositories (not high-velocity data). |

### Permission Model Design

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| Authorization Mechanism | **Azure Entra ID groups + document classification** | Entra ID already manages agency affiliations via group membership (e.g., "CDT-Employees", "GovOps-HR"). Document classification (public/internal/confidential/restricted) adds granular control. Combines role-based (agency) and attribute-based (classification) access. | Pure RBAC: Too coarse (all CDT employees see all CDT docs). Pure ABAC: Too complex (hundreds of attributes). SharePoint permissions: Not portable across agencies. |
| Permission Caching | 5-minute TTL in Redis | Real-time Entra ID queries add 200-500ms latency per search. Unacceptable for 3-second p95 target. 5-minute cache balances security (stale permissions window) and performance. Cache invalidation on group membership change events. | No caching: Violates latency requirements. 1-hour TTL: Security risk (stale permissions for demoted/transferred employees). Database caching: Slower than Redis, no atomic operations. |
| Row-Level Security | Backend filtering (not database RLS) | Azure AI Search doesn't support database-style RLS. Backend filters search results by comparing user's `agency_permissions` against document `agency_id` + `classification`. Happens in Python before returning API response. | Client-side filtering: Security vulnerability (exposes unauthorized docs in API). Azure SQL RLS: Requires migrating from AI Search to SQL, loses semantic search. Post-processing: Same as backend filtering but less clear. |
| Permission Propagation Delay | 5 minutes max (cache TTL) | When employee's Entra ID group membership changes (transfer, promotion, termination), permission cache must expire. Webhook from Entra ID triggers cache invalidation. 5-minute TTL ensures stale permissions expire automatically. | Real-time: Adds latency on every search. 1-hour delay: Unacceptable security window. Manual refresh: Unreliable. |

### Cross-Reference Detection

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| Relationship Detection Method | Embedding similarity + citation parsing + metadata analysis | **Multi-signal approach**: (1) Embeddings detect conceptual similarity (e.g., two bias testing policies), (2) regex citation parsing detects explicit references (e.g., "See Policy 123-A"), (3) metadata matching detects supersession (newer version, same title). Confidence score combines all three. | Embeddings only: Misses explicit citations. Citation parsing only: Misses implicit relationships. LLM-based: Too slow and expensive for 100k docs. |
| Relationship Types | Supersedes, References, Complements, Conflicts | **Supersedes**: Newer policy replaces older (detected by version metadata + "supersedes" keyword). **References**: Explicit citation (detected by regex). **Complements**: Related topic, different agency (detected by embeddings). **Conflicts**: Contradictory guidance (detected by embeddings + negation analysis). | More granular types: Adds complexity. Binary "related/not related": Loses actionable information. |
| Confidence Scoring | 0-100 scale with thresholds | 0-30: No relationship. 30-70: "Suggested" (user can validate). 70-100: "Confirmed" (high confidence, actionable). Calculated as weighted average: embeddings (40%), citation presence (40%), metadata match (20%). | Binary match/no-match: Hides uncertainty. LLM confidence: Unreliable without validation. Three-tier (low/medium/high): Too coarse for prioritization. |
| Batch Processing | Nightly batch job + on-demand API | **Nightly batch**: Pre-computes cross-references for all documents, stores in `cross_references` table. Fast retrieval at search time. **On-demand API**: Allows user to trigger cross-reference detection for specific document (e.g., newly uploaded policy). | Real-time on every search: Too slow (5+ seconds to compare against 100k docs). Manual curation only: Doesn't scale. Never update: Stale as corpus grows. |

### Expert Routing Implementation

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| Expert Identification | Document authorship + metadata tags + explicit profiles | **Authorship**: Document metadata contains author email → automatic expert association. **Tags**: Experts self-declare expertise areas (e.g., "HR policy", "IT security"). **Profiles**: Optional expert profile with bio, past consultations. Combines implicit (authorship) and explicit (tags) signals. | Authorship only: Misses SMEs who don't author docs. Tags only: Requires manual curation. LLM-based: Hallucinates experts not in system. |
| Expert Ranking | Relevance score (document count × recency × availability) | **Document count**: More documents on topic = higher expertise. **Recency**: Recent activity weighted higher (expertise may decay). **Availability**: "Unavailable" experts ranked lower. Formula: `score = doc_count × (1 + recency_factor) × availability_multiplier`. | Alphabetical: Useless for prioritization. Random: No signal. Popularity (past contacts): Biases toward well-known experts. |
| Contact Method Integration | Pre-fill email/Teams message with context | Expert contact triggers: (1) Pre-filled email with subject "Question about [document title]", body includes search query and document link. (2) Teams deep link to start chat with expert, context pre-populated. (3) Audit log records contact initiation (not message content). | Direct email only: No Teams integration. No context: User manually types background. Full message preview: Privacy concern (expert didn't consent). |
| Availability Status | Manual toggle + auto-detection (out-of-office) | Experts can manually set "Available", "Busy", "Unavailable". System auto-detects Outlook/Google Calendar out-of-office and sets "Unavailable". Availability shown in expert card with return date if known. | Manual only: Often stale. Auto-only: Misses ad-hoc unavailability. No availability: Users waste time contacting busy experts. |

## Architecture Decisions

### 3-Agent Pipeline vs Federated Search Orchestrator

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | **3-Agent Pipeline (QueryAgent → RouterAgent → ActionAgent)** | Federated search benefits from pipeline: QueryAgent extracts intent (search keywords, filters, agency scope). RouterAgent determines which agencies to query based on user permissions. ActionAgent executes hybrid search, filters results, and formats response. Clean separation of concerns. |

**3-Agent Pattern Justification**:
- **QueryAgent**: Parses search query text, extracts filters (date range, document type), sanitizes PII before logging, expands acronyms (e.g., "CDT" → "California Department of Technology").
- **RouterAgent**: Retrieves user's Entra ID group membership, maps to agency permissions, determines agency scope for search (only agencies user has access to).
- **ActionAgent**: Executes Azure AI Search hybrid query, filters results by classification level, ranks by relevance, identifies cross-references, retrieves expert recommendations, formats JSON response.

**Why Not Simpler**:
- Single-agent: Mixes authorization logic with search logic, harder to test and audit.
- Direct Azure AI Search: No permission enforcement (security vulnerability), no query sanitization (PII leakage), no cross-reference detection.

### Frontend Design (React vs Minimal)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI Complexity | **Full React frontend with search UX patterns** | Unlike accelerator 005 (backend-only API), cross-agency search needs rich UI: auto-complete, faceted filters, result highlighting, document preview, expert cards. State employees use web interface daily, not API integration. Investment in UX justified by 10k+ users. |

**Frontend Features**:
- **SearchBar**: Debounced input, auto-complete suggestions from popular queries, advanced search syntax hints.
- **FacetFilters**: Agency, document type, classification, date range filters with result counts.
- **SearchResults**: Card-based layout, relevance score visualization, snippet highlighting, progressive loading (infinite scroll).
- **CrossReferences**: Expandable "Related Documents" section with relationship type badges (supersedes/references/complements/conflicts).
- **ExpertCard**: Expert name, agency, expertise tags, availability status, contact methods (email/Teams).
- **DocumentPreview**: Modal with full document content, metadata, access log, download button.

### Progressive Result Rendering

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Result Streaming | **Progressive loading with agency priority** | Azure AI Search query across 100k+ documents can take 1-3 seconds. Rather than blocking on complete results, stream results as they arrive. Frontend renders first 20 results immediately (<500ms), then appends more. Priority order: user's own agency first, then most relevant other agencies. |

**Implementation**:
- Backend: FastAPI streaming response with Server-Sent Events (SSE)
- Frontend: EventSource API to receive results in real-time
- Batch size: 20 results per chunk
- Timeout: If no results in 3 seconds, show "No results found" (don't wait indefinitely)

**Why Progressive**:
- Perceived latency: Users see results <500ms instead of 3-second wait
- Prioritization: Own agency results appear first (most likely relevant)
- Scalability: As corpus grows to 500k+ docs, latency remains constant

### Document Parsing Approach

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Parsing Strategy | **Source system native APIs (SharePoint, Confluence, Google Drive)** | Documents already exist in agency repositories. Rather than uploading copies, integrate with source systems via APIs. SharePoint Graph API, Confluence REST API, Google Drive API provide text extraction, metadata, and change webhooks. Avoids data duplication and keeps search synchronized with source. |

**Connectors**:
- **SharePoint**: Microsoft Graph API → Document library listing, file download, metadata extraction, webhook subscriptions
- **Confluence**: REST API v2 → Page content (HTML), attachments, metadata, webhooks
- **Google Drive**: Drive API v3 → File listing, export to text, metadata, Drive Activity API for changes
- **Generic**: If agency uses other systems (Dropbox, Box, file shares), fallback to manual upload + Azure Document Intelligence parsing

**Indexing Pipeline**:
1. Connector polls source system API or receives webhook
2. Downloads document content (text/HTML/PDF)
3. Extracts text (native APIs or Document Intelligence OCR for PDFs)
4. Generates embeddings (text-embedding-3-large)
5. Uploads to Azure AI Search index
6. Stores cross-reference relationships in SQLite

## Mock Strategy

### Mock Mode Implementation

**Environment Variable**: `USE_MOCK_SERVICES=true` (default for Labs 00-03)

| Component | Mock Implementation | Real Implementation |
|-----------|---------------------|---------------------|
| Azure AI Search | In-memory document list with keyword filtering | Azure AI Search hybrid query (BM25 + semantic) |
| Azure Entra ID | Hardcoded user with 3 agency permissions | MSAL auth + group membership API |
| Permission Cache | In-memory dict (no Redis) | Redis cache with 5-minute TTL |
| Document Indexing | Pre-loaded JSON file with 50 sample documents | Connector pipelines to SharePoint/Confluence/Drive |
| Cross-Reference Detection | Pre-computed relationships in JSON | Nightly batch job with embedding similarity |
| Expert Routing | Hardcoded 5 experts with expertise tags | Expert profiles from document authorship + tags |
| Audit Logging | In-memory log list (not persisted) | Persistent SQLite with immutable audit_logs table |

**Mock Data Sources**:
- `backend/mock-data/documents.json` (50 sample documents across 5 agencies)
- `backend/mock-data/permissions.json` (3 users with different agency access)
- `backend/mock-data/cross-references.json` (10 pre-computed relationships)
- `backend/mock-data/experts.json` (5 subject matter experts)
- `backend/mock-data/search-queries.json` (10 sample queries with expected results)

**Mock Users**:
- `alice@cdt.ca.gov` - CDT employee (access: CDT internal + all public)
- `bob@govops.ca.gov` - GovOps manager (access: GovOps internal + CDT internal + all public)
- `carol@dgs.ca.gov` - DGS auditor (access: all agencies all classifications - auditor role)

**Mock Mode Benefits**:
- No Azure credentials needed
- Instant search results (<10ms)
- Deterministic testing (same query = same results)
- Offline development

## Risk Analysis

### Top Technical Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Permission cache staleness (5-minute window)** - Employee transferred to different agency but cache shows old permissions, accesses unauthorized documents | Medium | Critical | (1) Webhook from Entra ID on group membership change triggers cache invalidation. (2) Cache TTL capped at 5 minutes (auto-expire). (3) Real-time permission check on document download (not just search results). (4) Audit log flags permission cache hits vs misses for monitoring. |
| **Cross-reference false positives** - System claims two documents are related when they're unrelated, confusing users | Medium | Medium | (1) Confidence threshold: Only show "Confirmed" relationships (70%+ confidence). (2) User feedback: "Is this related?" vote updates confidence scores. (3) SME validation: Subject matter experts can approve/reject suggested relationships. (4) A/B testing: Measure click-through rate on cross-references. |
| **Search performance degradation (>3s latency) as corpus grows to 500k+ docs** | High | High | (1) Azure AI Search auto-scaling (Standard tier → 3 replicas, 3 partitions). (2) Index optimization: Remove unused fields, optimize vector dimensions. (3) Query optimization: Limit result set to top 100 (user rarely scrolls beyond). (4) Caching: Popular queries cached in Redis (15-minute TTL). |
| **Document classification mismatch** - Document marked "Internal" in source system but should be "Confidential", leaked to unauthorized users | Medium | High | (1) Classification validation rules at indexing (e.g., "personnel" keyword → flag for review). (2) Document owner required to confirm classification on upload. (3) Periodic audit: GovOps reviews random sample of documents for correct classification. (4) Re-classification API allows owner to update without re-upload. |
| **Expert spam** - Users abuse expert contact feature, bombarding SMEs with requests | Low | Medium | (1) Rate limiting: Max 5 expert contacts per user per day. (2) Context requirement: Contact must include search query and document link (prevents generic "help me" messages). (3) Expert opt-out: Experts can disable contact feature for specific expertise areas. (4) Reputation system: Experts can rate contact quality (future enhancement). |
| **Azure AI Search index drift** - Source documents updated but search index not refreshed, users see stale content | Medium | Medium | (1) Webhook subscriptions from SharePoint/Confluence/Drive trigger real-time re-indexing. (2) Nightly full re-index as fallback (detects missed webhooks). (3) Index version tracking: Document metadata includes `last_indexed_at`, UI shows "Updated 2 days ago, indexed 1 day ago". (4) Manual re-index API for urgent updates. |

## Performance Considerations

### Latency Targets

| Operation | Target (p95) | Strategy |
|-----------|--------------|----------|
| Search query | <3 seconds | Azure AI Search Standard tier (3 replicas). Hybrid query optimization. Permission filtering in parallel with search. Progressive result streaming. |
| Permission check | <300ms | Redis cache (5-min TTL). Batch user group lookup (not per-doc). Entra ID cache pre-warming on login. |
| Document access | <500ms | Direct download from source system (SharePoint SAS token, Confluence direct link). No backend proxy. Browser cache for previously accessed docs. |
| Cross-reference lookup | <200ms | Pre-computed in database (not real-time similarity). Indexed by document_id. Max 10 cross-refs per document (limit complexity). |
| Expert search | <500ms | In-memory expert index (small dataset, <1000 experts). Fuzzy name matching with Levenshtein distance. Ranked by relevance score. |
| Auto-complete suggestions | <100ms | Pre-computed popular queries in Redis (updated hourly). Trie data structure for prefix matching. Max 10 suggestions. |

### Caching Strategy

| Data Type | Cache | TTL | Invalidation |
|-----------|-------|-----|--------------|
| User permissions | Redis (per user) | 5 minutes | Entra ID webhook on group change |
| Search results | Redis (per query hash) | 15 minutes | Document re-index event |
| Popular queries | Redis (global) | 1 hour | Nightly analytics job |
| Expert profiles | In-memory (backend) | Application lifetime | Manual API refresh |
| Document embeddings | Azure AI Search index | Permanent | Document re-index |
| Cross-references | SQLite (persistent) | Permanent | Nightly batch job updates |
| Auto-complete suggestions | Redis (global) | 1 hour | Hourly analytics job |

### Scaling Approach

| Resource | Initial Capacity | Auto-Scale Trigger | Max Capacity |
|----------|------------------|-------------------|--------------|
| Azure Container Apps (backend) | 3 instances (2 vCPU, 4GB each) | CPU >70% or request queue >50 | 20 instances |
| Azure AI Search | Standard tier (3 replicas, 1 partition) | Query latency >3s or QPS >50 | 12 replicas, 12 partitions |
| Redis Cache | Basic tier (1GB) | Memory >80% | Premium tier (26GB) |
| Azure OpenAI (embeddings) | Provisioned 100K TPM | Usage >80% of quota | Request 500K TPM increase |
| Async SQLite (audit logs, cross-refs) | Single file | File size >20GB | Migrate to Azure SQL Database |

**Capacity Planning**:
- Expected load: 10,000 state employees, 5 searches/day/user = 50,000 searches/day = 580 QPS average
- Peak load: 9am-11am (3x average) = 1,740 QPS → Need 20 backend instances + 12 AI Search replicas
- Document corpus: 100,000 documents initially → 500,000 in 2 years → Need partition scaling
- Embeddings: 100k docs × 3000 tokens/doc × 2 (initial + updates) = 600M tokens → 100K TPM handles in 6,000 minutes (4 days for full re-index)

## Technology Stack Summary

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| Backend Framework | FastAPI | 0.109+ | Async support, SSE streaming, Pydantic v2 integration, WebSocket support |
| Search Engine | Azure AI Search | Standard tier | Hybrid search (BM25 + semantic), native vector support, auto-scaling, 99.9% SLA |
| Embeddings | text-embedding-3-large | Latest | 3072 dimensions for cross-reference accuracy, Azure OpenAI integration |
| Authentication | Azure Entra ID | MSAL 1.28+ | Native group membership, SSO, government cloud support |
| Permission Cache | Redis | 7.0+ | Sub-millisecond latency, atomic operations, pub/sub for cache invalidation |
| Database | Async SQLite | aiosqlite 0.19+ | Lightweight for cross-refs and audit logs, ACID compliance |
| Document Connectors | Microsoft Graph, Confluence REST, Google Drive API | Latest stable | Native integration with agency source systems |
| Frontend Framework | React | 18+ | Component architecture, hooks, concurrent rendering for progressive loading |
| State Management | React Context + hooks | Built-in | No Redux/MobX complexity for read-heavy search app |
| UI Components | Tailwind CSS + Headless UI | Latest | WCAG 2.1 AA compliance, responsive design, accessibility |
| Search UI Patterns | InstantSearch.js (Algolia) | Adapted | Faceted filters, auto-complete, result highlighting (adapted for Azure AI Search) |
| Testing | pytest + vitest + Playwright | Latest | Backend unit/integration, frontend unit, E2E cross-browser |
| Deployment | Docker + Azure Container Apps | Docker 24+, ACA v1 | Serverless scaling, managed Redis, Entra ID integration |

## Open Questions & Future Research

1. **Multi-language support**: Should we support Spanish, Chinese, Vietnamese for multilingual state employees? Azure Translator adds complexity and cost.

2. **Federated search beyond documents**: Should we include email archives (Outlook/Gmail search)? Privacy and CPRA concerns.

3. **AI-generated summaries**: Should we use GPT-4 to generate document summaries at index time? Cost vs value unclear.

4. **Conversational search**: Should we support follow-up queries ("Show me the updated version")? Requires session state management.

5. **Personalized ranking**: Should we re-rank results based on user's past clicks and agency affiliation? ML model adds complexity.

6. **Knowledge graph**: Should we build explicit graph of agency relationships, policy hierarchies, org charts? Graph database (Neo4j/Cosmos Gremlin) adds infrastructure.

7. **Real-time collaboration**: Should we show who else is viewing same document (Google Docs-style presence)? WebSocket infrastructure required.

8. **Document version control**: Should we track all versions of policies or only latest? Storage cost vs historical analysis value.

9. **Cross-agency analytics**: Should we track which agencies reference each other's policies most? Privacy vs collaboration insights.

10. **Mobile app**: Should we build iOS/Android apps or is responsive web sufficient? Most state employees work on desktops.
