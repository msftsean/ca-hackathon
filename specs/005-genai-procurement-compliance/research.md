# Technology Research: GenAI Procurement Compliance Checker

**Feature**: `005-genai-procurement-compliance`  
**Created**: 2024-12-19  
**Purpose**: Technology decisions and architecture research for vendor AI attestation compliance analysis system

## Technology Choices

### Azure OpenAI Model Selection

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| Primary LLM | GPT-4 Turbo (128k context) | Need large context window to process 50-page attestation documents in single request. High accuracy required for compliance determination (90%+ agreement with human experts). | GPT-3.5 Turbo: Insufficient accuracy for nuanced compliance language. Claude 2: Not available in Azure gov cloud. GPT-4o: More expensive, speed not critical for 5-minute target. |
| Embedding Model | text-embedding-3-large (3072 dimensions) | Highest quality embeddings for semantic similarity in cross-reference detection. Required for NIST AI RMF risk classification matching. | text-embedding-ada-002: Lower dimension (1536), insufficient for complex policy similarity. text-embedding-3-small: 50% cheaper but reduces cross-reference accuracy below 70% threshold. |
| Function Calling | GPT-4 with Semantic Kernel plugins | Structured output required for compliance results (status, evidence, confidence). Semantic Kernel provides native Azure integration and template management. | Direct JSON mode: Less reliable schema adherence. LangChain: Adds Python dependency complexity. Custom prompt engineering: Not maintainable as requirements change. |

### Document Processing Strategy

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| PDF Parsing | pypdf + Azure Document Intelligence | pypdf handles digital-native PDFs (80% of cases). Document Intelligence OCR for scanned/image PDFs (20% of cases). Two-tier approach optimizes cost ($0.001/page for DI). | pypdf only: Fails on scanned documents. Document Intelligence only: $50-100/month unnecessary cost for digital PDFs. pdfplumber: Similar to pypdf but less maintained. |
| DOCX Parsing | python-docx library | Native Python library, handles 95% of DOCX formats. No external dependencies or API costs. | Azure Document Intelligence: Overkill for DOCX, adds latency. docx2txt: Text-only, loses formatting/structure. mammoth: More complex, not needed. |
| Text Chunking | Semantic chunking (512 tokens, 20% overlap) | Compliance requirements often span multiple paragraphs. Semantic chunking preserves context better than fixed-size. 20% overlap prevents evidence loss at boundaries. | Fixed-size chunks: Splits mid-sentence, breaks context. Paragraph chunking: Inconsistent size, some paragraphs are 2000+ tokens. Page chunking: Too coarse, loses granularity. |

### Compliance Rule Evaluation

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| Rule Engine | Semantic Kernel with custom plugins | Declarative rule templates in JSON + Semantic Kernel prompt engineering. Allows non-engineers to update rules when regulations change. Version control for audit trail. | Hard-coded prompts: Not maintainable. LangChain agents: Overcomplicated for deterministic evaluation. Azure AI Search filter queries: Cannot handle nuanced language matching. |
| Confidence Scoring | 0-100 scale with multi-factor calculation | Combines: (1) keyword match count, (2) semantic similarity score, (3) evidence excerpt length, (4) negation detection. Flags <85% for human review per FR-024. | Binary match/no-match: Hides uncertainty. LLM confidence only: Unreliable without validation signals. |
| Evidence Extraction | Named regex + GPT-4 summarization | Regex identifies candidate sections (e.g., "bias testing", "civil rights compliance"). GPT-4 summarizes matching paragraphs to 200-char evidence excerpts. | Full-text evidence: Too verbose for UI. Regex only: Misses paraphrased compliance language. GPT-4 only: Hallucinates evidence not in document. |

### Scoring & Gap Analysis

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| Severity Weighting | Critical=40 pts, High=30 pts, Medium=20 pts, Low=10 pts per rule | Linear weighted sum to 100-point scale. Critical gaps (e.g., civil rights violations) are disqualifying (score <60). Aligns with CDT legal review thresholds. | Unweighted average: Treats all gaps equally, obscures critical failures. Multiplicative penalty: Too harsh, single low gap tanks entire score. |
| Gap Prioritization | Severity tier → Evidence confidence → Remediation complexity | Sort gaps by: (1) critical/high/medium/low, (2) high-confidence gaps first (confident findings actionable), (3) easy-to-fix gaps last (quick wins). | Alphabetical: Useless for decision-making. Score impact: Misleading, low-severity gaps have low impact by design. |
| Remediation Guidance | Template-based suggestion engine | Each ComplianceRule has `remediation_template` field with vendor-ready language. GPT-4 customizes template with attestation context. Reduces vendor clarification cycles by 40% (SC-012). | Generic advice: Not actionable. Full GPT-4 generation: Inconsistent quality, potential hallucinations. No remediation: Vendors don't know how to fix gaps. |

### Cross-Reference Implementation

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| SB 53 Mapping | Keyword + scope detection | SB 53 applies to "automated decision systems" affecting legal/financial status. Detect keywords (e.g., "credit score", "benefit determination") + GPT-4 scope check. Binary trigger (applies / does not apply). | Full SB 53 analysis: Redundant with EO N-5-26 overlap. No SB 53 check: Legal liability if missed. Embeddings similarity: Too fuzzy for legal trigger determination. |
| NIST AI RMF Classification | Risk tier decision tree + impact assessment | 4-tier classification: (1) minimal risk (productivity tools), (2) limited risk (internal analytics), (3) high risk (public-facing decisions), (4) unacceptable risk (prohibited uses). GPT-4 evaluates impact + sector + population. | Manual classification: Inconsistent across vendors. Pre-defined categories: Misses novel AI systems. Embeddings only: Lacks decision logic. |
| Overlap Detection | Requirement text similarity + logical deduplication | ComplianceRule entities have `overlaps_with` field. When same evidence satisfies multiple rules (e.g., EO N-5-26 "bias testing" + NIST RMF "fairness evaluation"), flag as consolidated compliance. | No deduplication: Confuses vendors with redundant requirements. Automatic merge: Loses traceability to original regulations. |

## Architecture Decisions

### Single vs Multi-Agent Pipeline

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | **Single-agent with orchestration** (not 3-agent pipeline) | Compliance analysis is deterministic rule evaluation, not conversational workflow. No routing logic needed (all attestations follow same evaluation path). ActionAgent would just call compliance analyzer service. Simpler = more reliable for legal compliance. |

**3-Agent Pattern Not Used Because**:
- **No QueryAgent needed**: No user intent detection or entity extraction. Input is structured (uploaded document + procurement_id).
- **No RouterAgent needed**: No multi-path routing. Every attestation goes through identical analysis pipeline: parse → extract → evaluate rules → score → generate gaps.
- **No ActionAgent complexity**: Final output is deterministic (ComplianceResult set + GapAnalysis report), not dynamic response generation.

### Backend-Only Design (No Frontend)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI Layer | **API-only backend, no React frontend** | Procurement officers use existing tools (CaleProcure, FI$Cal). Integration via REST API endpoints is preferred over separate web UI. Reduces development scope by 40%. Mock mode provides curl-based testing. |

**Why No Frontend**:
- Existing procurement systems (CaleProcure, FI$Cal) already have vendor management UIs
- CDT procurement team prefers API integration to workflow switching
- Compliance reports exported as PDF/DOCX for review in existing document systems
- Audit log queries via admin API, not user-facing dashboard
- Saves 12-15 React components, authentication UI, state management complexity

### Synchronous vs Asynchronous Processing

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Analysis Mode | **Synchronous with progress polling** | 95% of attestations analyze in <5 minutes (FR-022). Synchronous HTTP request with Server-Sent Events (SSE) for progress updates. Simpler than async job queue for procurement officer workflow. |

**Implementation**:
- POST `/attestations/{id}/analyze` returns 202 Accepted with `analysis_id`
- GET `/attestations/{id}/analysis-status` returns progress percentage + current stage
- SSE endpoint `/attestations/{id}/analysis-stream` for real-time updates
- If analysis exceeds 5 minutes (large documents, OCR required), falls back to async with email notification

### Document Parsing Approach

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Parsing Flow | **Tiered: pypdf → Document Intelligence (fallback) → Human review (failure)** | Optimizes cost and latency. 80% of documents are digital PDFs (pypdf = free + <10s). 15% are scanned/image PDFs (Document Intelligence OCR = $0.001/page + 30-60s). 5% are malformed (flag for human review). |

**Failure Handling**:
- pypdf failure (exception, blank text, <100 chars extracted) → Try Document Intelligence
- Document Intelligence failure (low confidence, OCR errors) → Set status=`requires_human_review`, notify assigned officer
- Parsing timeout (>2 minutes) → Fail fast, require officer to resubmit in different format

## Mock Strategy

### Mock Mode Implementation

**Environment Variable**: `USE_MOCK_SERVICES=true` (default for Labs 00-03)

| Component | Mock Implementation | Real Implementation |
|-----------|---------------------|---------------------|
| Document Upload | Save to `backend/mock-data/attestations/` local folder | Azure Blob Storage with SAS tokens |
| Document Parsing | Pre-extracted text files in `backend/mock-data/parsed/` | pypdf + Azure Document Intelligence OCR |
| Compliance Analysis | GPT-4 responses from `backend/mock-data/compliance-results.json` | Azure OpenAI GPT-4 Turbo API |
| Scoring Engine | Fixed scores from mock data (vendor A=85, vendor B=62) | Real severity-weighted calculation |
| Gap Analysis | Pre-generated gap reports from `backend/mock-data/gap-analysis.json` | Real gap detection + remediation generation |
| Report Export | Template-based PDF/DOCX with mock data | Real jinja2 templates with analysis results |
| Audit Logging | In-memory log list (not persisted) | Async SQLite with immutable audit_records table |

**Mock Data Sources**:
- `backend/mock-data/attestations/vendor-a-complete.pdf` (compliant attestation, score 95)
- `backend/mock-data/attestations/vendor-b-gaps.pdf` (non-compliant, score 62, critical gaps)
- `backend/mock-data/attestations/vendor-c-partial.docx` (partial compliance, score 78)
- `backend/mock-data/compliance-rules.json` (EO N-5-26 + SB 53 + NIST rules)
- `backend/mock-data/compliance-results.json` (pre-computed ComplianceResult entities)
- `backend/mock-data/gap-analysis.json` (pre-computed GapAnalysis entities)

**Mock Mode Benefits**:
- No Azure credentials required for local dev or workshops (Labs 00-03)
- Deterministic results for testing (same input = same output)
- Instant analysis (<100ms vs 2-5 minutes real analysis)
- Offline development capability

## Risk Analysis

### Top Technical Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **GPT-4 hallucinated compliance findings** (AI claims vendor complies with requirement not actually addressed) | High | Critical | (1) Confidence scoring flags <85% for human review. (2) Evidence extraction forces model to cite text excerpts, no paraphrasing. (3) Validation test set with ground truth (50 attestations reviewed by legal experts). (4) Human-in-the-loop override with mandatory justification (FR-019). |
| **Document parsing failures** (scanned PDFs, handwritten notes, non-standard formats) | Medium | High | (1) Tiered parsing (pypdf → Document Intelligence → human review). (2) Pre-upload validation (file format, size, minimum text extraction). (3) Clear error messages with actionable guidance. (4) Manual upload fallback for procurement officers. |
| **Regulatory requirement changes mid-procurement** (EO N-5-26 updated, new SB 53 provisions) | Medium | High | (1) ComplianceRule versioning with effective_date and sunset_date. (2) Attestation analysis tagged with rule_version used. (3) Re-analysis API endpoint to apply updated rules. (4) Notification to procurement officers when rules change during active procurement. |
| **Severity weighting disagreement with legal review** (system scores 85, legal counsel says disqualifying) | Medium | Medium | (1) Pilot with CDT legal counsel to calibrate severity weights. (2) 80% acceptance rate target (SC-006) allows 20% override. (3) Procurement officers can override AI score with justification. (4) Feedback loop: Legal overrides update severity weights in future releases. |
| **Vendor attestation gaming** (vendors copy compliance language without implementation) | High | Medium | (1) System detects boilerplate language (exact matches across vendors). (2) Evidence quality scoring (generic statements score lower than specific details). (3) Procurement officers required to verify high-risk claims (critical gaps). (4) Audit trail flags suspiciously perfect attestations for extra scrutiny. |
| **Performance degradation with 50 concurrent analyses** (FR-025) | Low | Medium | (1) Async processing with queue management (Celery + Redis). (2) Azure OpenAI provisioned throughput (dedicated TPM quota). (3) Load testing during development. (4) Auto-scaling Azure Container Apps (2-10 instances). |

## Performance Considerations

### Latency Targets

| Operation | Target (p95) | Strategy |
|-----------|--------------|----------|
| Document upload | <2 seconds | Direct upload to Azure Blob Storage (not through backend). Pre-signed SAS tokens. Async metadata extraction. |
| Document parsing | <30 seconds | pypdf in-memory parsing (<10s). Document Intelligence for OCR (<30s). Parallel page processing. |
| Compliance analysis | <5 minutes | GPT-4 batch processing (all rules in single prompt). Parallel rule evaluation for large documents. |
| Gap report generation | <10 seconds | jinja2 templating with pre-computed GapAnalysis. WeasyPrint for PDF rendering (CPU-bound). |
| API response (GET) | <300ms | Async SQLite with prepared statements. Database indexes on attestation_id, procurement_id, status. |
| Vendor comparison (up to 10 vendors) | <2 seconds | Pre-computed scores in GapAnalysis table. No real-time recalculation. |

### Caching Strategy

| Data Type | Cache | TTL | Invalidation |
|-----------|-------|-----|--------------|
| ComplianceRule entities | In-memory dict | Application lifetime | Manual (admin API endpoint to reload rules) |
| Azure OpenAI responses | None | N/A | Not cached (compliance analysis must be fresh for audit trail) |
| Document parsing results | Database (VendorAttestation.metadata) | Permanent | Never (immutable after initial parse) |
| User permissions (RBAC) | Redis cache | 5 minutes | On Entra ID group membership change |
| Blob Storage SAS tokens | In-memory | 50 minutes | Regenerate before expiration |

### Scaling Approach

| Resource | Initial Capacity | Auto-Scale Trigger | Max Capacity |
|----------|------------------|-------------------|--------------|
| Azure Container Apps (backend) | 2 instances (2 vCPU, 4GB each) | CPU >70% or queue depth >20 | 10 instances |
| Azure OpenAI (GPT-4) | Provisioned 50K TPM | Usage >80% of quota | Request 200K TPM increase |
| Azure Blob Storage | Standard tier | N/A (effectively unlimited) | Premium tier if IOPS >20K |
| Async SQLite (audit logs) | Single file | File size >10GB | Migrate to Azure SQL Database |
| Document Intelligence | Pay-per-use | N/A | Request quota increase if >10K pages/day |

**Capacity Planning**:
- Expected load: 500-1000 attestations/year across 200 agencies = 2-3 attestations/day average
- Peak load during procurement cycles: 50 concurrent analyses = 10 instances needed
- GPT-4 usage: 50 pages × 3000 tokens/page × 18 rules = ~2.7M tokens/attestation → 50K TPM handles 1 attestation every 3 minutes, need 200K TPM for 50 concurrent

## Technology Stack Summary

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| Backend Framework | FastAPI | 0.109+ | Async support, Pydantic v2 integration, OpenAPI auto-generation, fastest Python framework |
| AI Orchestration | Semantic Kernel | 1.0+ | Native Azure OpenAI integration, plugin architecture for compliance rules, template management |
| LLM | Azure OpenAI GPT-4 Turbo | 1106-preview | 128k context window, function calling, highest accuracy for compliance language |
| Embeddings | text-embedding-3-large | Latest | 3072 dimensions for cross-reference detection, NIST AI RMF classification |
| Document Parsing | pypdf + python-docx | Latest stable | Digital PDF/DOCX parsing, no external dependencies |
| OCR Fallback | Azure Document Intelligence | v3.1 | Scanned PDF support, structured output, $0.001/page cost-effective |
| Storage (docs) | Azure Blob Storage | v12 SDK | Secure document storage, SAS tokens, 7-year retention compliance |
| Storage (data) | Async SQLite | aiosqlite 0.19+ | Lightweight for <10k attestations/year, ACID compliance for audit trail |
| Report Generation | jinja2 + WeasyPrint | Latest | PDF/DOCX export, template-based, WCAG 2.1 AA compliance |
| Authentication | Azure Entra ID | MSAL 1.28+ | SSO integration, RBAC via group membership, government cloud support |
| Testing | pytest + httpx | Latest | Async test support, FastAPI integration, contract testing |
| Deployment | Docker + Azure Container Apps | Docker 24+, ACA v1 | Serverless scaling, managed infrastructure, Azure integration |

## Open Questions & Future Research

1. **GPT-4 vs GPT-4o cost-benefit**: Is 2x cost justified by potential accuracy improvement? Need validation study with legal counsel reviews.

2. **Custom fine-tuning**: Should we fine-tune GPT-4 on historical attestation reviews? Requires 50+ human-labeled examples, unclear ROI.

3. **Compliance rule versioning UX**: How do procurement officers handle attestation analyzed with old rules? Re-analysis vs. grandfather clause?

4. **Multi-language support**: Should we support non-English attestations (international vendors)? Azure Translator integration adds complexity.

5. **Blockchain audit trail**: Is immutable SQLite sufficient or should we use blockchain for tamper-proof audit logs? Legal requirement unclear.

6. **Real-time collaboration**: Do multiple procurement officers need to review same attestation simultaneously? Would require WebSocket/SignalR.

7. **Integration testing strategy**: How to test CaleProcure/FI$Cal API integration without access to staging environments? Mock server vs. manual QA?
