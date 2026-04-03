# Data Model: EDD Claims Assistant (007-edd-claims-assistant)

**Phase**: 1 — Entity definitions  
**Author**: Mouse (Tester/Spec Creator)  
**Date**: 2026-04-02  
**Feature**: Natural language Q&A for UI, DI, and PFL claims with voice support

Patterns follow the existing codebase:
- **Backend**: Pydantic v2 with `Field(...)`, `field_validator`, `Literal` types — matches `backend/app/models/schemas.py`
- **Enums**: `str, Enum` subclasses — matches `backend/app/models/enums.py`
- **Frontend**: TypeScript interfaces and `enum` — matches `frontend/src/` conventions

---

## Backend Entities — Pydantic v2

### Enumerations

```python
# backend/app/models/edd_enums.py

from enum import Enum


class ClaimType(str, Enum):
    """EDD claim types."""
    UI = "ui"  # Unemployment Insurance
    DI = "di"  # Disability Insurance
    PFL = "pfl"  # Paid Family Leave


class ClaimStatus(str, Enum):
    """Current processing status of a claim."""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    DENIED = "denied"
    APPEALED = "appealed"
    CLOSED = "closed"


class EligibilityResult(str, Enum):
    """Pre-screening eligibility assessment result."""
    LIKELY_ELIGIBLE = "likely_eligible"
    POSSIBLY_ELIGIBLE = "possibly_eligible"
    LIKELY_INELIGIBLE = "likely_ineligible"
    NEEDS_REVIEW = "needs_review"


class EmploymentType(str, Enum):
    """Claimant's employment classification."""
    W2_EMPLOYEE = "w2_employee"
    CONTRACTOR_1099 = "contractor_1099"
    MILITARY = "military"
    FEDERAL_EMPLOYEE = "federal_employee"
    SELF_EMPLOYED = "self_employed"


class EscalationPriority(str, Enum):
    """Urgency level for escalation tickets."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, Enum):
    """Type of support ticket."""
    STATUS_INQUIRY = "status_inquiry"
    ELIGIBILITY_QUESTION = "eligibility_question"
    APPEAL = "appeal"
    TECHNICAL_ISSUE = "technical_issue"
    ESCALATION = "escalation"
    GENERAL_QUESTION = "general_question"
```

---

### Claim

Represents a UI, DI, or PFL claim with current status and pending actions.

```python
# backend/app/models/edd_schemas.py

from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class Claim(BaseModel):
    """A UI, DI, or PFL claim with status and payment information."""

    claim_id: str = Field(..., description="Unique claim identifier (e.g., UI-2024-123456)")
    claimant_id: str = Field(..., description="Claimant's unique identifier (hashed for privacy)")
    type: ClaimType = Field(..., description="Claim type: UI, DI, or PFL")
    status: ClaimStatus = Field(..., description="Current processing status")
    filed_date: date = Field(..., description="Date claim was filed")
    weekly_benefit_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Weekly benefit amount in USD (if approved)"
    )
    next_payment_date: Optional[date] = Field(
        None,
        description="Next scheduled payment date (if approved and active)"
    )
    last_certification_date: Optional[date] = Field(
        None,
        description="Most recent bi-weekly certification submission"
    )
    pending_issues: List[str] = Field(
        default_factory=list,
        description="List of issues blocking payment (e.g., 'ID Verification', 'Employer Response')"
    )
    required_actions: List[str] = Field(
        default_factory=list,
        description="Actions claimant must take (e.g., 'Submit pay stubs', 'Complete ID.me verification')"
    )
    total_paid: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Total amount paid to date"
    )
    claim_balance: Optional[Decimal] = Field(
        None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Remaining benefit balance"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("claim_id")
    @classmethod
    def validate_claim_id(cls, v: str) -> str:
        """Ensure claim ID follows EDD format."""
        if not v or len(v) < 5:
            raise ValueError("claim_id must be at least 5 characters")
        return v
```

---

### ClaimTypeMetadata

Defines metadata for each claim type (UI, DI, PFL) including eligibility rules and required documents.

```python
class ClaimTypeMetadata(BaseModel):
    """Metadata for a claim type (UI, DI, PFL)."""

    type_id: ClaimType = Field(..., description="Claim type identifier")
    name: str = Field(..., description="Human-readable name (e.g., 'Unemployment Insurance')")
    description: str = Field(..., description="Brief description of the benefit")
    required_documents: List[str] = Field(
        ...,
        description="Base document list (e.g., ['SSN', 'ID', 'Employment verification'])"
    )
    eligibility_criteria: List[str] = Field(
        ...,
        description="High-level eligibility requirements (e.g., 'Worked in CA in last 18 months')"
    )
    typical_processing_time_days: int = Field(
        ...,
        ge=1,
        description="Typical processing time in days"
    )
    max_weekly_benefit: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Maximum weekly benefit amount in USD"
    )
    max_benefit_weeks: int = Field(
        ...,
        ge=1,
        description="Maximum number of weeks benefits can be claimed"
    )
    policy_url: str = Field(..., description="Link to official EDD policy page")
```

---

### EligibilityAssessment

Records the result of a pre-screening eligibility assessment.

```python
class EligibilityFactor(BaseModel):
    """A single factor contributing to eligibility determination."""

    factor: str = Field(..., description="Factor name (e.g., 'work_history', 'separation_reason')")
    meets_requirement: bool = Field(..., description="True if factor supports eligibility")
    explanation: str = Field(..., description="Human-readable explanation")


class EligibilityAssessment(BaseModel):
    """Pre-screening eligibility assessment result."""

    assessment_id: str = Field(..., description="Unique assessment ID")
    claimant_id: Optional[str] = Field(None, description="Claimant ID if authenticated")
    session_id: str = Field(..., description="Conversation session ID")
    claim_type: ClaimType = Field(..., description="Claim type being assessed")
    result: EligibilityResult = Field(..., description="Preliminary eligibility result")
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the assessment (0.0 to 1.0)"
    )
    factors: List[EligibilityFactor] = Field(
        ...,
        description="List of factors considered in the assessment"
    )
    recommended_action: str = Field(
        ...,
        description="Next step for claimant (e.g., 'Proceed with filing', 'Contact EDD for review')"
    )
    disclaimer: str = Field(
        default="This is a preliminary assessment. Final eligibility is determined by EDD after you file.",
        description="Legal disclaimer for assessment"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### SupportTicket

Tracks escalations and support requests.

```python
class SupportTicket(BaseModel):
    """Escalation or support ticket with conversation context."""

    ticket_id: str = Field(..., description="Unique ticket identifier")
    claim_id: Optional[str] = Field(None, description="Associated claim ID if applicable")
    claimant_id: Optional[str] = Field(None, description="Claimant ID if authenticated")
    session_id: str = Field(..., description="Conversation session ID")
    category: TicketCategory = Field(..., description="Type of ticket")
    priority: EscalationPriority = Field(..., description="Urgency level")
    status: str = Field(default="open", description="Ticket status (open, assigned, resolved, closed)")
    assigned_to: Optional[str] = Field(None, description="Agent ID if assigned")
    conversation_transcript: List[dict] = Field(
        default_factory=list,
        description="Full conversation history (list of message dicts)"
    )
    escalation_reason: Optional[str] = Field(
        None,
        description="Why this was escalated (e.g., 'Explicit human request', 'Policy ambiguity')"
    )
    notes: List[str] = Field(
        default_factory=list,
        description="Internal agent notes"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(None, description="When ticket was resolved")
```

---

### PolicyArticle

Represents an article in the EDD policy knowledge base.

```python
class PolicyArticle(BaseModel):
    """EDD policy knowledge base article."""

    article_id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., min_length=1, max_length=500, description="Article title")
    content: str = Field(..., min_length=10, description="Full article text (markdown supported)")
    category: str = Field(..., description="Category (e.g., 'UI Filing', 'DI Benefits', 'PFL Eligibility')")
    claim_types: List[ClaimType] = Field(
        default_factory=list,
        description="Relevant claim types (UI, DI, PFL)"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Search tags (e.g., 'eligibility', 'weekly-certification', 'appeal')"
    )
    effective_date: date = Field(..., description="When this policy became effective")
    expiration_date: Optional[date] = Field(None, description="When this policy expires (if applicable)")
    citations: List[str] = Field(
        default_factory=list,
        description="Official EDD policy references (e.g., 'UI Code Section 1253(c)')"
    )
    policy_url: str = Field(..., description="Link to official EDD policy page")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="False if article is archived")
```

---

### ConversationSession

Manages chat and voice session state.

```python
class ConversationMessage(BaseModel):
    """A single message in a conversation."""

    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text")
    modality: str = Field(default="text", description="'text' or 'voice'")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationSession(BaseModel):
    """Chat or voice conversation session."""

    session_id: str = Field(..., description="Unique session identifier")
    claimant_id: Optional[str] = Field(None, description="Claimant ID if authenticated")
    modality: str = Field(default="text", description="Current modality: 'text', 'voice', or 'hybrid'")
    messages: List[ConversationMessage] = Field(
        default_factory=list,
        description="Conversation history"
    )
    escalated: bool = Field(default=False, description="True if escalated to human")
    escalation_ticket_id: Optional[str] = Field(None, description="Associated ticket ID if escalated")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Session expiration time")
```

---

### DocumentChecklist

Generates personalized document lists based on claim type and claimant situation.

```python
class DocumentItem(BaseModel):
    """A single required document."""

    name: str = Field(..., description="Document name (e.g., 'Most recent pay stub')")
    description: str = Field(..., description="Why it's needed and where to get it")
    required: bool = Field(..., description="True if absolutely required, False if optional")
    applies_to: List[str] = Field(
        default_factory=list,
        description="Employment types or situations this applies to (e.g., ['w2_employee', 'contractor_1099'])"
    )


class DocumentChecklist(BaseModel):
    """Personalized document checklist for a claim."""

    checklist_id: str = Field(..., description="Unique checklist ID")
    claim_type: ClaimType = Field(..., description="Claim type (UI, DI, PFL)")
    employment_type: EmploymentType = Field(..., description="Claimant's employment classification")
    special_circumstances: List[str] = Field(
        default_factory=list,
        description="Special flags (e.g., 'union_member', 'military_discharge', 'multiple_employers')"
    )
    documents: List[DocumentItem] = Field(..., description="List of required/optional documents")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### IdentityVerification

Securely validates claimant identity for claim lookups.

```python
class IdentityVerification(BaseModel):
    """Identity verification attempt for secure claim lookup."""

    verification_id: str = Field(..., description="Unique verification ID")
    session_id: str = Field(..., description="Associated session ID")
    verification_method: str = Field(
        default="last4_ssn_dob",
        description="Verification method (e.g., 'last4_ssn_dob', 'idme', 'logingovca')"
    )
    success: bool = Field(..., description="True if verification succeeded")
    attempt_count: int = Field(default=1, ge=1, le=5, description="Number of verification attempts")
    lockout_until: Optional[datetime] = Field(
        None,
        description="If locked out, when can they try again"
    )
    verified_at: Optional[datetime] = Field(None, description="When verification succeeded")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("attempt_count")
    @classmethod
    def validate_attempts(cls, v: int) -> int:
        """Enforce max 5 attempts."""
        if v > 5:
            raise ValueError("Maximum 5 verification attempts allowed")
        return v
```

---

## Frontend Entities — TypeScript

### Enumerations

```typescript
// frontend/src/types/edd.ts

export enum ClaimType {
  UI = 'ui',
  DI = 'di',
  PFL = 'pfl',
}

export enum ClaimStatus {
  PENDING = 'pending',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  DENIED = 'denied',
  APPEALED = 'appealed',
  CLOSED = 'closed',
}

export enum EligibilityResult {
  LIKELY_ELIGIBLE = 'likely_eligible',
  POSSIBLY_ELIGIBLE = 'possibly_eligible',
  LIKELY_INELIGIBLE = 'likely_ineligible',
  NEEDS_REVIEW = 'needs_review',
}

export enum EmploymentType {
  W2_EMPLOYEE = 'w2_employee',
  CONTRACTOR_1099 = 'contractor_1099',
  MILITARY = 'military',
  FEDERAL_EMPLOYEE = 'federal_employee',
  SELF_EMPLOYED = 'self_employed',
}
```

---

### Interfaces

```typescript
export interface Claim {
  claim_id: string;
  claimant_id: string;
  type: ClaimType;
  status: ClaimStatus;
  filed_date: string; // ISO date
  weekly_benefit_amount: number | null;
  next_payment_date: string | null; // ISO date
  last_certification_date: string | null; // ISO date
  pending_issues: string[];
  required_actions: string[];
  total_paid: number | null;
  claim_balance: number | null;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}

export interface EligibilityFactor {
  factor: string;
  meets_requirement: boolean;
  explanation: string;
}

export interface EligibilityAssessment {
  assessment_id: string;
  claimant_id: string | null;
  session_id: string;
  claim_type: ClaimType;
  result: EligibilityResult;
  confidence_score: number; // 0.0 to 1.0
  factors: EligibilityFactor[];
  recommended_action: string;
  disclaimer: string;
  created_at: string; // ISO datetime
}

export interface SupportTicket {
  ticket_id: string;
  claim_id: string | null;
  claimant_id: string | null;
  session_id: string;
  category: string;
  priority: string;
  status: string;
  assigned_to: string | null;
  conversation_transcript: Array<Record<string, unknown>>;
  escalation_reason: string | null;
  notes: string[];
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
  resolved_at: string | null; // ISO datetime
}

export interface PolicyArticle {
  article_id: string;
  title: string;
  content: string; // Markdown
  category: string;
  claim_types: ClaimType[];
  tags: string[];
  effective_date: string; // ISO date
  expiration_date: string | null; // ISO date
  citations: string[];
  policy_url: string;
  last_updated: string; // ISO datetime
  is_active: boolean;
}

export interface DocumentItem {
  name: string;
  description: string;
  required: boolean;
  applies_to: string[];
}

export interface DocumentChecklist {
  checklist_id: string;
  claim_type: ClaimType;
  employment_type: EmploymentType;
  special_circumstances: string[];
  documents: DocumentItem[];
  generated_at: string; // ISO datetime
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  modality: 'text' | 'voice';
  timestamp: string; // ISO datetime
}

export interface ConversationSession {
  session_id: string;
  claimant_id: string | null;
  modality: 'text' | 'voice' | 'hybrid';
  messages: ConversationMessage[];
  escalated: boolean;
  escalation_ticket_id: string | null;
  created_at: string; // ISO datetime
  last_activity_at: string; // ISO datetime
  expires_at: string | null; // ISO datetime
}
```

---

## Mock Data Samples

### Mock Claims (backend/mocks/edd_claims.json)

```json
[
  {
    "claim_id": "UI-2024-123456",
    "claimant_id": "claimant_abc123",
    "type": "ui",
    "status": "approved",
    "filed_date": "2024-01-15",
    "weekly_benefit_amount": 450.00,
    "next_payment_date": "2024-04-10",
    "last_certification_date": "2024-04-01",
    "pending_issues": [],
    "required_actions": ["Complete bi-weekly certification by April 14"],
    "total_paid": 5400.00,
    "claim_balance": 6300.00,
    "created_at": "2024-01-15T08:30:00Z",
    "updated_at": "2024-04-02T10:15:00Z"
  },
  {
    "claim_id": "DI-2024-789012",
    "claimant_id": "claimant_xyz789",
    "type": "di",
    "status": "pending",
    "filed_date": "2024-03-20",
    "weekly_benefit_amount": null,
    "next_payment_date": null,
    "last_certification_date": null,
    "pending_issues": ["Medical certification required", "Employer response pending"],
    "required_actions": ["Submit completed medical certification (DE 2501) from your doctor"],
    "total_paid": null,
    "claim_balance": null,
    "created_at": "2024-03-20T14:22:00Z",
    "updated_at": "2024-03-25T09:45:00Z"
  }
]
```

### Mock Policy Article (backend/mocks/edd_policies.json)

```json
[
  {
    "article_id": "policy_ui_filing_001",
    "title": "How to File for Unemployment Insurance Benefits",
    "content": "To file for Unemployment Insurance (UI) in California, you must:\n\n1. Have earned wages during your base period\n2. Be unemployed or working reduced hours through no fault of your own\n3. Be able and available to work\n4. Actively seek work each week\n\nYou can file online at [edd.ca.gov/UI_Online](https://edd.ca.gov/UI_Online) or by calling 1-800-300-5616.",
    "category": "UI Filing",
    "claim_types": ["ui"],
    "tags": ["filing", "eligibility", "how-to"],
    "effective_date": "2023-01-01",
    "expiration_date": null,
    "citations": ["UI Code Section 1253", "22 CCR § 1253(c)-1"],
    "policy_url": "https://edd.ca.gov/en/Unemployment/Filing_a_Claim/",
    "last_updated": "2024-01-10T00:00:00Z",
    "is_active": true
  }
]
```

---

## Notes

- **PII Handling**: All `claimant_id` values are hashed. SSN and DOB are never stored in session logs. `IdentityVerification` uses last 4 SSN + DOB for verification but does not store the values.
- **Session Expiration**: `ConversationSession.expires_at` defaults to 30 minutes of inactivity. After expiration, session context is cleared but conversation history is archived for compliance.
- **Voice Integration**: Reuses `VoiceMessage` and `VoiceSession` models from 002-voice-interaction. Voice transcript entries are appended to `ConversationSession.messages` with `modality: "voice"`.
- **Mock Data Coverage**: Mock JSON includes 20+ sample claims across all types (UI/DI/PFL) and statuses, 50+ policy articles covering common questions, and 10+ eligibility rule decision trees.
