# Data Model: Cross-Agency Knowledge Hub

**Feature**: `006-cross-agency-knowledge-hub`  
**Created**: 2024-12-19  
**Purpose**: Entity definitions and relationships for permission-aware federated search across California state agency knowledge bases

## Core Entities

### SearchQuery

Represents user search request with query text, filters, and result metadata.

**Attributes**:
- `query_id` (UUID, primary key): Unique identifier for search query
- `user_id` (str, required): Azure Entra ID user identifier (email or object ID)
- `user_agency` (str, required): User's primary agency affiliation
- `user_role` (enum, required): User's role at time of search - `employee`, `manager`, `auditor`, `admin`
- `query_text` (str, required): Raw search query text (max 500 chars)
- `sanitized_query` (str, required): Sanitized query with PII removed, used for logging
- `query_type` (enum, default: simple): Query complexity - `simple`, `advanced`, `boolean`, `phrase`
- `agency_scope` (list[str], required): List of agency IDs included in search scope (based on user permissions)
- `filters` (JSON, optional): Applied facet filters (agency, document_type, classification, date_range)
- `page` (int, default: 1): Result page number for pagination
- `page_size` (int, default: 20): Results per page (max 100)
- `sort_by` (enum, default: relevance): Sort order - `relevance`, `date_desc`, `date_asc`, `title_asc`
- `result_count` (int, optional): Total number of results returned
- `response_time_ms` (int, optional): Query execution time in milliseconds
- `search_method` (enum, default: hybrid): Search algorithm - `hybrid`, `keyword`, `semantic`
- `top_result_score` (float, optional): Highest relevance score in results
- `zero_results` (bool, default: False): Flag for queries returning no results
- `suggestions_provided` (list[str], optional): "Did you mean?" suggestions offered
- `clicked_result_ids` (list[str], optional): Document IDs user clicked from results (for analytics)
- `timestamp` (datetime, required): When query was executed
- `ip_address` (str, required): IPv4/IPv6 address of request origin
- `user_agent` (str, optional): Browser/client user agent string
- `session_id` (UUID, optional): User session identifier for query grouping
- `metadata` (JSON, optional): Additional query metadata (A/B test variant, feature flags)

**Relationships**:
- Many-to-one with `AuditLog`: Each search query generates audit log entry
- Many-to-many with `Document`: Search results link queries to documents (via click tracking)

**Indexes**:
- Primary: `query_id`
- Secondary: `user_id`, `timestamp`, `user_agency`, `zero_results`
- Composite: `(user_id, timestamp)` for user search history
- Full-text: `query_text` for query analytics

**Privacy & Security**:
- `sanitized_query` used for logging to prevent PII exposure in audit trails
- `query_text` encrypted at rest and not included in CPRA disclosures
- Retention: 90 days for analytics, then purged (except `sanitized_query` kept for 7 years in audit log)

---

### Document

Represents indexed document from agency repository with metadata and classification.

**Attributes**:
- `document_id` (UUID, primary key): Unique identifier for document
- `agency_id` (str, required): Agency that owns document (e.g., `CDT`, `DGS`, `GovOps`)
- `agency_name` (str, required): Human-readable agency name (e.g., "California Department of Technology")
- `title` (str, required): Document title (max 500 chars)
- `content` (str, required): Full text content for indexing (max 100MB)
- `content_hash` (str, required): SHA-256 hash of content for change detection
- `summary` (str, optional): AI-generated summary (max 1000 chars)
- `document_type` (enum, required): Document category - `policy`, `procedure`, `guideline`, `form`, `memo`, `report`, `faq`, `training`, `other`
- `classification` (enum, required): Access classification - `public`, `internal`, `confidential`, `restricted`
- `classification_justification` (str, optional): Reason for classification level (for auditing)
- `source_url` (str, optional): Original document URL in source repository
- `source_system` (str, optional): Source system identifier (e.g., `SharePoint`, `Confluence`, `Google Drive`)
- `file_format` (str, optional): Original file format (PDF, DOCX, HTML, TXT)
- `author` (str, optional): Document author (may be expert contact)
- `author_email` (str, optional): Author contact email
- `owner` (str, optional): Current document owner/maintainer
- `created_at` (datetime, optional): Document creation date (from metadata)
- `last_modified_at` (datetime, optional): Last modification date (from metadata)
- `indexed_at` (datetime, required): When document was indexed in AI Search
- `re_indexed_at` (datetime, optional): Last re-indexing timestamp
- `version` (str, optional): Document version number
- `supersedes_document_id` (UUID, optional): Reference to previous version of document
- `superseded_by_document_id` (UUID, optional): Reference to newer version of document
- `tags` (list[str], optional): User-defined or AI-generated tags for categorization
- `keywords` (list[str], optional): Key terms extracted from content
- `language` (str, default: en): Document language (ISO 639-1 code)
- `word_count` (int, optional): Document length in words
- `read_time_minutes` (int, optional): Estimated reading time
- `access_count` (int, default: 0): Number of times document has been accessed
- `last_accessed_at` (datetime, optional): Most recent access timestamp
- `requires_training` (bool, default: False): Flag for documents requiring completion tracking
- `expiration_date` (date, optional): Date when document becomes obsolete
- `review_date` (date, optional): Next scheduled review date
- `status` (enum, default: active): Document status - `active`, `archived`, `superseded`, `draft`, `under_review`
- `metadata` (JSON, optional): Additional document metadata (retention policy, approval chain)

**Relationships**:
- Many-to-many with `AgencyPermission`: Document access controlled by agency permissions
- One-to-many with `CrossReference`: Document may be source or target of cross-references
- Many-to-many with `Expert`: Documents may be associated with subject matter experts
- Many-to-many with `SearchQuery`: Documents appear in search results (via click tracking)
- Self-referential: `supersedes_document_id` and `superseded_by_document_id` create version chain

**Indexes** (Azure AI Search):
- Primary: `document_id`
- Searchable: `title`, `content`, `summary`, `tags`, `keywords` (full-text + semantic)
- Filterable: `agency_id`, `document_type`, `classification`, `status`, `created_at`, `last_modified_at`
- Facetable: `agency_id`, `document_type`, `classification`, `tags`
- Retrievable: All fields except `content` (content snippets only in search results)

**Security**:
- `classification` enforced at search time via permission filtering
- `content` field only accessible to users with appropriate `AgencyPermission`
- Document deletion creates tombstone record (soft delete) for audit purposes

---

### AgencyPermission

Represents user's access rights to specific agency with role-based permissions.

**Attributes**:
- `permission_id` (UUID, primary key): Unique identifier for permission record
- `user_id` (str, required): Azure Entra ID user identifier
- `agency_id` (str, required): Agency identifier (e.g., `CDT`, `DGS`)
- `role` (enum, required): User's role within agency - `employee`, `manager`, `hr`, `legal`, `it_admin`, `executive`, `contractor`
- `access_level` (enum, required): Permission level - `none`, `public_only`, `internal`, `confidential`, `restricted`
- `granted_at` (datetime, required): When permission was granted
- `granted_by` (str, required): Administrator who granted permission
- `expires_at` (datetime, optional): Permission expiration date (for temporary access)
- `revoked_at` (datetime, optional): When permission was revoked (soft delete)
- `revoked_by` (str, optional): Administrator who revoked permission
- `revocation_reason` (str, optional): Justification for revocation
- `source` (enum, required): How permission was determined - `entra_id_group`, `manual_assignment`, `role_inheritance`, `temporary_grant`
- `entra_group_id` (str, optional): Azure Entra ID group ID if permission comes from group membership
- `can_share` (bool, default: False): Whether user can share documents with external users
- `can_export` (bool, default: False): Whether user can export/download documents
- `can_annotate` (bool, default: False): Whether user can add comments/notes to documents
- `metadata` (JSON, optional): Additional permission metadata (justification, approval workflow)

**Relationships**:
- Many-to-one with user (via `user_id` in Azure Entra ID)
- Many-to-many with `Document`: Permissions determine document access
- One-to-many with `AuditLog`: Permission changes generate audit events

**Indexes**:
- Primary: `permission_id`
- Unique: `(user_id, agency_id)` for active permissions (where `revoked_at IS NULL`)
- Secondary: `user_id`, `agency_id`, `access_level`, `expires_at`, `revoked_at`
- Composite: `(user_id, access_level)` for permission queries

**Caching**:
- User permissions cached for 5 minutes after Entra ID lookup
- Cache invalidated on permission change, role change, or explicit logout
- Cache key: `user_permissions:{user_id}`

**Permission Hierarchy**:
```
restricted > confidential > internal > public_only > none
```
Higher access level grants access to all lower levels (e.g., `confidential` includes `internal` and `public_only`).

**Lifecycle**:
- Permissions synced from Entra ID group membership every 5 minutes
- Expired permissions (`expires_at < now()`) automatically treated as revoked
- Revoked permissions preserved for audit trail but excluded from permission checks

---

### CrossReference

Represents detected relationship between two documents across agencies.

**Attributes**:
- `reference_id` (UUID, primary key): Unique identifier for cross-reference
- `source_document_id` (UUID, foreign key, required): Document being referenced from
- `target_document_id` (UUID, foreign key, required): Document being referenced to
- `relationship_type` (enum, required): Type of relationship - `supersedes`, `superseded_by`, `references`, `referenced_by`, `complements`, `conflicts_with`, `duplicate`, `related`
- `confidence_score` (float, 0.0-1.0, required): AI confidence in this relationship
- `detection_method` (enum, required): How relationship was found - `citation_analysis`, `content_similarity`, `metadata_matching`, `manual_validation`, `url_link`
- `similarity_score` (float, 0.0-1.0, optional): Semantic similarity score if detected via content analysis
- `citation_text` (str, optional): Exact citation text if detected via citation analysis
- `citation_location` (str, optional): Location in source document where citation appears (page/section)
- `bidirectional` (bool, default: False): Whether relationship is symmetric (e.g., `related` is bidirectional, `supersedes` is not)
- `validated` (bool, default: False): Whether relationship was confirmed by human reviewer
- `validated_by` (str, optional): User who validated relationship
- `validated_at` (datetime, optional): When validation occurred
- `rejected` (bool, default: False): Whether relationship was marked as false positive
- `rejected_by` (str, optional): User who rejected relationship
- `rejected_reason` (str, optional): Why relationship was rejected
- `detected_at` (datetime, required): When relationship was first detected
- `relevance_context` (str, optional): Explanation of why documents are related (for UI display)
- `metadata` (JSON, optional): Additional detection metadata (algorithm version, features used)

**Relationships**:
- Many-to-one with `Document` (source): Cross-reference originates from source document
- Many-to-one with `Document` (target): Cross-reference points to target document
- Bidirectional relationships create two records (source→target and target→source)

**Indexes**:
- Primary: `reference_id`
- Secondary: `source_document_id`, `target_document_id`, `relationship_type`, `confidence_score`, `validated`
- Composite: `(source_document_id, target_document_id, relationship_type)` unique constraint
- Filter: `confidence_score >= 0.7 AND rejected = False` for displaying cross-references

**Detection Pipeline**:
1. **Citation Analysis**: Parse document text for explicit references (e.g., "See Policy CDT-2024-01")
2. **Content Similarity**: Compute semantic similarity between document embeddings (threshold: 0.75)
3. **Metadata Matching**: Compare titles, keywords, tags for overlap (threshold: 3+ shared terms)
4. **URL Link Detection**: Extract and resolve hyperlinks in document content
5. **Manual Validation**: Allow users to suggest cross-references for expert review

**Confidence Thresholds**:
- High confidence (>0.85): Display automatically in UI
- Medium confidence (0.70-0.85): Display as "Suggested" relationship
- Low confidence (<0.70): Require human validation before displaying

---

### Expert

Represents subject matter expert available for consultation and collaboration.

**Attributes**:
- `expert_id` (UUID, primary key): Unique identifier for expert
- `user_id` (str, unique, required): Azure Entra ID user identifier
- `full_name` (str, required): Expert's full name
- `email` (str, unique, required): Primary contact email
- `agency_id` (str, required): Expert's home agency
- `agency_name` (str, required): Human-readable agency name
- `department` (str, optional): Department or division within agency
- `job_title` (str, required): Expert's job title
- `expertise_areas` (list[str], required): Declared expertise topics (e.g., ["cybersecurity", "data privacy", "AI governance"])
- `expertise_keywords` (list[str], optional): Additional keywords extracted from authored documents
- `biography` (str, optional): Brief professional biography (max 500 chars)
- `certifications` (list[str], optional): Professional certifications (e.g., ["CISSP", "PMP", "California Bar"])
- `languages` (list[str], default: ["en"]): Languages spoken (ISO 639-1 codes)
- `contact_preference` (enum, default: email): Preferred contact method - `email`, `teams`, `phone`, `no_contact`
- `phone` (str, optional): Phone number for urgent consultation
- `teams_handle` (str, optional): Microsoft Teams username
- `profile_url` (str, optional): Link to agency directory profile or LinkedIn
- `availability_status` (enum, required): Current availability - `available`, `busy`, `out_of_office`, `unavailable`, `retired`
- `max_concurrent_consultations` (int, default: 3): Maximum consultations expert can handle simultaneously
- `current_consultation_count` (int, default: 0): Number of active consultations assigned
- `total_consultations_completed` (int, default: 0): Lifetime consultation count
- `average_response_time_hours` (float, optional): Average time to respond to consultation request
- `expert_rating` (float, 0.0-5.0, optional): Average rating from consultation feedback
- `rating_count` (int, default: 0): Number of ratings received
- `authored_document_count` (int, default: 0): Number of documents expert has authored
- `last_active_at` (datetime, optional): Most recent document authored or consultation completed
- `opt_in_directory` (bool, default: True): Whether expert appears in public directory
- `allow_external_contact` (bool, default: False): Whether non-agency users can contact expert
- `created_at` (datetime, required): Expert profile creation timestamp
- `updated_at` (datetime, required): Profile last update timestamp
- `metadata` (JSON, optional): Additional expert metadata (publications, awards, specializations)

**Relationships**:
- One-to-one with user (via `user_id` in Azure Entra ID)
- Many-to-many with `Document`: Experts associated with documents they authored or reviewed
- Many-to-many with `SearchQuery`: Expert recommendations appear in search results

**Indexes**:
- Primary: `expert_id`
- Unique: `user_id`, `email`
- Secondary: `agency_id`, `availability_status`, `opt_in_directory`
- Full-text: `expertise_areas`, `expertise_keywords`, `biography` for expert search
- Composite: `(agency_id, availability_status)` for agency expert lookup

**Expert Ranking Algorithm**:
```
relevance_score = (
    query_match_score * 0.4 +          # How well expertise matches query
    document_count * 0.2 +               # Number of relevant documents authored
    recency_score * 0.2 +                # Recent activity (last_active_at)
    rating_score * 0.1 +                 # User ratings
    availability_bonus * 0.1             # Availability status multiplier
)
```

**Privacy Controls**:
- Experts can opt out of directory (`opt_in_directory = False`)
- Contact information only visible to users with agency access (unless `allow_external_contact = True`)
- Consultation history aggregated only (no details of individual consultations)

---

### AuditLog

Represents immutable log entry for search, access, and collaboration events.

**Attributes**:
- `log_id` (UUID, primary key): Unique identifier for audit log entry
- `event_type` (enum, required): Type of event - `search_query`, `document_accessed`, `document_downloaded`, `expert_contacted`, `cross_reference_validated`, `permission_granted`, `permission_revoked`, `user_login`, `user_logout`, `unauthorized_access_attempt`
- `user_id` (str, required): Azure Entra ID user identifier
- `user_agency` (str, required): User's agency at time of event
- `user_role` (enum, required): User's role at time of event
- `ip_address` (str, required): IPv4/IPv6 address of request origin
- `user_agent` (str, optional): Browser/client user agent string
- `action` (str, required): Human-readable description of action
- `resource_type` (enum, required): Type of resource affected - `search_query`, `document`, `expert`, `permission`, `cross_reference`
- `resource_id` (str, required): Identifier of affected resource
- `document_id` (UUID, optional): Reference to document if event relates to document access
- `query_id` (UUID, optional): Reference to search query if event relates to search
- `expert_id` (UUID, optional): Reference to expert if event relates to expert contact
- `search_query_text` (str, optional): Sanitized search query text (for search events)
- `result_count` (int, optional): Number of results returned (for search events)
- `access_granted` (bool, required): Whether action was authorized (True) or blocked (False)
- `denial_reason` (str, optional): Why access was denied (if `access_granted = False`)
- `classification_level` (str, optional): Classification of accessed resource
- `timestamp` (datetime, required): When event occurred (microsecond precision)
- `response_time_ms` (int, optional): Request processing time
- `success` (bool, required): Whether action completed successfully
- `error_message` (str, optional): Error details if `success = False`
- `session_id` (UUID, optional): User session identifier for event correlation
- `correlation_id` (UUID, optional): Distributed tracing correlation ID
- `record_hash` (str, required): SHA-256 hash of record content for tamper detection
- `previous_record_hash` (str, optional): Hash of previous audit record (blockchain-like chain)
- `metadata` (JSON, optional): Additional event context (feature flags, A/B test variants)

**Relationships**:
- Many-to-one with `SearchQuery`: Audit logs reference search queries
- Many-to-one with `Document`: Audit logs reference document access events
- Many-to-one with `Expert`: Audit logs reference expert contact events
- Self-referential: `previous_record_hash` links to prior record for integrity chain

**Indexes**:
- Primary: `log_id`
- Secondary: `user_id`, `event_type`, `timestamp`, `document_id`, `access_granted`
- Composite: `(user_id, timestamp)` for user activity timeline
- Composite: `(document_id, timestamp)` for document access history
- Composite: `(event_type, timestamp)` for event-type filtering
- Filter: `access_granted = False` for security monitoring

**Immutability**:
- No UPDATE or DELETE operations permitted via API
- Database triggers prevent direct modification
- Record hash verification detects tampering
- Retention: 7 years per California Public Records Act

**Chain Integrity**:
```
record_hash = SHA256(
    event_type + user_id + timestamp + action + resource_id + 
    access_granted + previous_record_hash
)
```
Any modification breaks hash chain, enabling tamper detection.

**CPRA Compliance**:
- Audit logs support California Public Records Act requests
- PII redaction applied before disclosure (user_id mapped to redacted identifier)
- Sensitive search queries (`search_query_text`) reviewed for privacy before disclosure
- Export format: CSV with standard fields, JSON metadata available on request

---

## Entity Relationships Summary

```
SearchQuery (1) ──── (many) AuditLog
SearchQuery (many) ──── (many) Document [via search results]

Document (many) ──── (many) AgencyPermission [access control]
Document (1) ──── (many) CrossReference [as source]
Document (1) ──── (many) CrossReference [as target]
Document (many) ──── (many) Expert [via authorship]
Document (1) ──── (many) AuditLog [via access events]
Document (0..1) ──── (1) Document [self-referential supersedes/superseded_by]

AgencyPermission (many) ──── (1) User [via Azure Entra ID]
AgencyPermission (1) ──── (many) AuditLog [permission change events]

CrossReference (many) ──── (1) Document [source]
CrossReference (many) ──── (1) Document [target]

Expert (1) ──── (1) User [via Azure Entra ID]
Expert (many) ──── (many) Document [via authorship]
Expert (1) ──── (many) AuditLog [via contact events]

AuditLog (0..1) ──── (1) AuditLog [self-referential hash chain]
```

## Azure AI Search Index Schema

**Document Index**: `documents-index`

```json
{
  "name": "documents-index",
  "fields": [
    {"name": "document_id", "type": "Edm.String", "key": true},
    {"name": "agency_id", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "agency_name", "type": "Edm.String", "filterable": true},
    {"name": "title", "type": "Edm.String", "searchable": true, "analyzer": "en.microsoft"},
    {"name": "content", "type": "Edm.String", "searchable": true, "analyzer": "en.microsoft"},
    {"name": "summary", "type": "Edm.String", "searchable": true},
    {"name": "document_type", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "classification", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "tags", "type": "Collection(Edm.String)", "searchable": true, "filterable": true, "facetable": true},
    {"name": "keywords", "type": "Collection(Edm.String)", "searchable": true},
    {"name": "author", "type": "Edm.String", "searchable": true, "filterable": true},
    {"name": "created_at", "type": "Edm.DateTimeOffset", "filterable": true, "sortable": true},
    {"name": "last_modified_at", "type": "Edm.DateTimeOffset", "filterable": true, "sortable": true},
    {"name": "indexed_at", "type": "Edm.DateTimeOffset", "filterable": true},
    {"name": "status", "type": "Edm.String", "filterable": true},
    {"name": "content_vector", "type": "Collection(Edm.Single)", "dimensions": 1536, "vectorSearchProfile": "vector-profile"}
  ],
  "vectorSearch": {
    "algorithms": [
      {"name": "vector-config", "kind": "hnsw"}
    ],
    "profiles": [
      {"name": "vector-profile", "algorithm": "vector-config"}
    ]
  },
  "semantic": {
    "configurations": [
      {
        "name": "semantic-config",
        "prioritizedFields": {
          "titleField": {"fieldName": "title"},
          "contentFields": [{"fieldName": "content"}, {"fieldName": "summary"}],
          "keywordsFields": [{"fieldName": "tags"}, {"fieldName": "keywords"}]
        }
      }
    ]
  }
}
```

**Hybrid Search Query**:
- Keyword search (BM25) on `title`, `content`, `summary`, `tags`, `keywords`
- Semantic search on `content_vector` (Azure OpenAI embeddings)
- Results combined using Reciprocal Rank Fusion (RRF)
- Filtering by `agency_id` (based on user permissions), `classification`, `document_type`, `created_at`

## Data Retention & Lifecycle

**Retention Policies**:
- `SearchQuery`: 90 days (analytics), then purged (sanitized query preserved in `AuditLog` for 7 years)
- `Document`: Indefinite (managed by source repositories), tombstone record preserved for 7 years after deletion
- `AgencyPermission`: 7 years after revocation (for audit purposes)
- `CrossReference`: Indefinite (unless both source and target documents are deleted)
- `Expert`: Active while employed, archived 7 years after separation
- `AuditLog`: 7 years minimum per CPRA, permanent retention recommended for forensic capability

**Lifecycle States**:
1. User authenticates → `AgencyPermission` records cached (5-minute TTL)
2. User searches → `SearchQuery` created, results filtered by permissions
3. User accesses document → `AuditLog.document_accessed` event created
4. Background job detects cross-references → `CrossReference` records created
5. Document updated in source → Re-indexed in Azure AI Search within 5 minutes
6. Permission revoked → Permission cache invalidated, future searches exclude affected documents
7. After 7 years → Cold storage archival (Azure Archive tier)

## Security & Compliance

**Encryption**:
- At rest: AES-256 for all database fields, Azure AI Search index data, and blob storage
- In transit: TLS 1.3 for all API communications, Azure service connections
- Search queries: PII sanitized before logging to audit trail

**Access Control**:
- Document-level permissions enforced via `AgencyPermission` lookup
- Row-level security on audit logs (users see only their own actions unless auditor role)
- Expert contact information visible only to users with agency access
- Role-based access:
  - `employee`: Search within permitted agencies, access permitted documents
  - `manager`: Same as employee + view team member audit logs
  - `auditor`: Read-only access to all audit logs, permission records
  - `admin`: Full access to indexing, permission management, expert directory

**Audit Requirements**:
- All search queries logged to `AuditLog` (with sanitized query text)
- All document accesses logged with user, timestamp, document, access method
- All expert contacts logged with user, expert, timestamp, contact method
- Failed authorization attempts logged with denial reason
- Audit log integrity verified via hash chain on application startup

**Data Classification** (per document `classification` field):
- `public`: Accessible to all authenticated state employees
- `internal`: Accessible only to employees of owning agency
- `confidential`: Accessible only to specific roles within agency (manager+, HR, legal)
- `restricted`: Accessible only by explicit permission grant (executive, legal, specific individuals)

**Query Sanitization**:
- Remove PII patterns: SSN (###-##-####), email addresses, phone numbers
- Remove sensitive terms: password, credential, secret, private key
- Log sanitized query only (original query encrypted, not logged)
- Flag queries containing potential PII for security review

**Permission Enforcement Flow**:
```
1. User authenticates → Retrieve Entra ID group memberships
2. Map groups to AgencyPermission records → Cache for 5 minutes
3. User searches → Build permission filter (agency_id IN permitted_agencies AND classification <= user_access_level)
4. Execute search with filter → Azure AI Search enforces document-level filtering
5. Return results → Only documents passing permission filter
6. User accesses document → Verify permission at access time (not just search time)
7. Log access → Create AuditLog.document_accessed event
```

**Compliance Checkpoints**:
- ✅ California Public Records Act: Audit logs support CPRA requests with privacy controls
- ✅ Information Practices Act: PII sanitized in logs, user consent for expert directory
- ✅ Envision 2026 Goal 4: Enables cross-agency collaboration and knowledge sharing
- ✅ CDT Security Standards: Encryption, access control, audit logging per CDT requirements
