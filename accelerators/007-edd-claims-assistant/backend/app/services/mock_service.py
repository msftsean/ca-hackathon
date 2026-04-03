"""Mock service returning sample EDD claims data."""

from datetime import datetime, timedelta
from app.models.schemas import (
    ClaimStatus,
    DocumentItem,
    EligibilityAssessment,
    IdentityVerification,
    PolicyArticle,
)


def _now():
    return datetime.now()


CLAIMS_DB: dict[str, dict] = {
    "UI": {
        "claim_id": "UI-2025-1234567",
        "claim_type": "UI",
        "status": "active",
        "filed_date": (_now() - timedelta(days=45)).isoformat(),
        "last_certified": (_now() - timedelta(days=3)).isoformat(),
        "weekly_benefit_amount": 450.00,
        "remaining_balance": 8550.00,
        "pending_issues": [],
        "next_payment_date": (_now() + timedelta(days=4)).isoformat(),
    },
    "UI-pending": {
        "claim_id": "UI-2025-2345678",
        "claim_type": "UI",
        "status": "pending",
        "filed_date": (_now() - timedelta(days=10)).isoformat(),
        "last_certified": None,
        "weekly_benefit_amount": 0.00,
        "remaining_balance": 0.00,
        "pending_issues": ["Identity verification required", "Employer response pending"],
        "next_payment_date": None,
    },
    "UI-denied": {
        "claim_id": "UI-2025-3456789",
        "claim_type": "UI",
        "status": "denied",
        "filed_date": (_now() - timedelta(days=30)).isoformat(),
        "last_certified": None,
        "weekly_benefit_amount": 0.00,
        "remaining_balance": 0.00,
        "pending_issues": ["Voluntary quit — insufficient cause"],
        "next_payment_date": None,
    },
    "DI": {
        "claim_id": "DI-2025-7654321",
        "claim_type": "DI",
        "status": "active",
        "filed_date": (_now() - timedelta(days=21)).isoformat(),
        "last_certified": (_now() - timedelta(days=7)).isoformat(),
        "weekly_benefit_amount": 620.00,
        "remaining_balance": 15480.00,
        "pending_issues": [],
        "next_payment_date": (_now() + timedelta(days=7)).isoformat(),
    },
    "PFL": {
        "claim_id": "PFL-2025-9876543",
        "claim_type": "PFL",
        "status": "on_hold",
        "filed_date": (_now() - timedelta(days=14)).isoformat(),
        "last_certified": None,
        "weekly_benefit_amount": 540.00,
        "remaining_balance": 4320.00,
        "pending_issues": ["Awaiting employer confirmation"],
        "next_payment_date": None,
    },
}


ELIGIBILITY_RULES: dict[str, dict] = {
    "UI": {
        "claim_type": "UI",
        "likely_eligible": True,
        "confidence": 0.85,
        "factors": [
            "Must have earned wages in base period (first 4 of last 5 completed quarters)",
            "Must be unemployed through no fault of your own",
            "Must be able and available to work",
        ],
        "requirements": [
            "Earned at least $1,300 in highest-paid quarter of base period",
            "Employed for at least 18 months in base period",
            "Lost job through no fault of your own (layoff, reduction in force)",
            "Physically able to work and available for full-time employment",
            "Actively searching for work each week",
        ],
        "next_steps": [
            "File your claim online at edd.ca.gov",
            "Gather your last employer's information",
            "Register with CalJOBS (caljobs.ca.gov)",
            "Certify for benefits every two weeks",
        ],
    },
    "DI": {
        "claim_type": "DI",
        "likely_eligible": True,
        "confidence": 0.80,
        "factors": [
            "Must have current SDI coverage through payroll deductions",
            "Must have a medical condition preventing work",
            "Must be under care of a licensed physician",
        ],
        "requirements": [
            "Currently covered by State Disability Insurance (SDI)",
            "Earned at least $300 in base period",
            "Unable to perform regular or customary work for at least 8 days",
            "Under care and treatment of a licensed physician or practitioner",
            "Filed claim within 49 days of becoming disabled",
        ],
        "next_steps": [
            "Obtain physician's certification of disability",
            "File your DI claim online at edd.ca.gov",
            "Submit medical records from treating physician",
            "Wait 7-day unpaid waiting period before benefits start",
        ],
    },
    "PFL": {
        "claim_type": "PFL",
        "likely_eligible": True,
        "confidence": 0.82,
        "factors": [
            "Must have earned at least $300 from which SDI deductions were withheld",
            "Must need time off for qualifying reason (bonding, care, military assist)",
            "Must have 12 months of contributions to SDI fund",
        ],
        "requirements": [
            "Contributed to SDI in past 12 months",
            "Earned at least $300 in base period",
            "Need time off to bond with new child, care for seriously ill family member, or military assist",
            "Cannot perform regular work during leave period",
        ],
        "next_steps": [
            "Notify your employer of your intent to take PFL",
            "File your PFL claim online at edd.ca.gov",
            "Provide certification (birth certificate, medical records, or military documentation)",
            "Wait for claim processing (typically 2-3 weeks)",
        ],
    },
}


DOCUMENT_CHECKLISTS: dict[str, list[dict]] = {
    "UI": [
        {"name": "Government-issued Photo ID", "required": True, "submitted": False, "description": "Driver's license, state ID, or passport"},
        {"name": "Social Security Card", "required": True, "submitted": False, "description": "Or document showing SSN"},
        {"name": "Last Employer Information", "required": True, "submitted": False, "description": "Name, address, dates of employment, reason for separation"},
        {"name": "Wage Records", "required": False, "submitted": False, "description": "Pay stubs from the last 18 months"},
        {"name": "DD-214", "required": False, "submitted": False, "description": "If you served in the military in the last 18 months"},
    ],
    "DI": [
        {"name": "Physician's Certificate", "required": True, "submitted": False, "description": "Completed by your treating physician (DE 2525XX)"},
        {"name": "Government-issued Photo ID", "required": True, "submitted": False, "description": "Driver's license, state ID, or passport"},
        {"name": "Medical Records", "required": True, "submitted": False, "description": "Diagnosis, treatment plan, and expected return-to-work date"},
        {"name": "Employer Information", "required": True, "submitted": False, "description": "Current employer name and contact information"},
    ],
    "PFL": [
        {"name": "Government-issued Photo ID", "required": True, "submitted": False, "description": "Driver's license, state ID, or passport"},
        {"name": "Birth Certificate or Adoption Papers", "required": True, "submitted": False, "description": "For bonding claims only"},
        {"name": "Medical Certification", "required": True, "submitted": False, "description": "For care claims — physician's statement about family member's condition"},
        {"name": "Employer Notification", "required": True, "submitted": False, "description": "Proof that employer was notified of leave"},
        {"name": "Military Documentation", "required": False, "submitted": False, "description": "For military assist claims only"},
    ],
}


POLICY_ARTICLES_DB: list[dict] = [
    {
        "article_id": "POL-UI-001",
        "title": "UI Eligibility Requirements",
        "content": "To be eligible for UI benefits, you must have earned sufficient wages during the base period and be unemployed through no fault of your own.",
        "claim_types": ["UI"],
        "last_updated": "2024-06-01T00:00:00",
    },
    {
        "article_id": "POL-UI-002",
        "title": "UI Certification Process",
        "content": "Claimants must certify for benefits every two weeks. Certification can be done online through UI Online or by mail using the paper form.",
        "claim_types": ["UI"],
        "last_updated": "2024-07-15T00:00:00",
    },
    {
        "article_id": "POL-DI-001",
        "title": "DI Coverage and Benefits",
        "content": "State Disability Insurance provides short-term partial wage replacement to eligible California workers who are unable to work due to a non-work-related illness, injury, or pregnancy.",
        "claim_types": ["DI"],
        "last_updated": "2024-05-20T00:00:00",
    },
    {
        "article_id": "POL-PFL-001",
        "title": "PFL Qualifying Reasons",
        "content": "Paid Family Leave provides up to 8 weeks of benefit payments to workers who need time off to care for a seriously ill family member, bond with a new child, or participate in qualifying military events.",
        "claim_types": ["PFL"],
        "last_updated": "2024-08-10T00:00:00",
    },
    {
        "article_id": "POL-GEN-001",
        "title": "Appeal Rights and Procedures",
        "content": "If your claim is denied, you have the right to appeal within 20 calendar days of the mailing date on the notice. Appeals are heard by an Administrative Law Judge.",
        "claim_types": ["UI", "DI", "PFL"],
        "last_updated": "2024-04-01T00:00:00",
    },
]


FILING_STEPS: dict[str, list[str]] = {
    "UI": [
        "Go to edd.ca.gov and select 'File a UI Claim'",
        "Create or log in to your Benefit Programs Online account",
        "Provide your personal information (SSN, address, contact)",
        "Enter your last employer's information (name, address, dates, reason for separation)",
        "Provide wage information for the last 18 months",
        "Select your preferred payment method (EDD Debit Card or direct deposit)",
        "Review and submit your claim",
        "Register with CalJOBS within 21 days",
        "Certify for benefits every two weeks",
    ],
    "DI": [
        "Obtain a physician's certificate of your disability",
        "Go to edd.ca.gov and select 'File a DI Claim'",
        "Log in to your SDI Online account",
        "Complete the claimant portion of the form",
        "Have your physician complete the medical certification",
        "Submit the claim and supporting documents",
        "Wait for claim processing (typically 14 days)",
    ],
    "PFL": [
        "Notify your employer at least 30 days in advance (if foreseeable)",
        "Go to edd.ca.gov and select 'File a PFL Claim'",
        "Log in to your SDI Online account",
        "Provide your personal and employer information",
        "Select your qualifying reason (bonding, care, or military assist)",
        "Submit required documentation (birth certificate, medical certification, etc.)",
        "Wait for claim processing (typically 2-3 weeks)",
    ],
}


class MockEDDService:
    """Returns mock EDD claim data for development and testing."""

    def get_claim(self, claim_type: str) -> ClaimStatus | None:
        data = CLAIMS_DB.get(claim_type)
        if not data:
            return None
        return ClaimStatus(
            claim_id=data["claim_id"],
            claim_type=data["claim_type"],
            status=data["status"],
            filed_date=datetime.fromisoformat(data["filed_date"]),
            last_certified=datetime.fromisoformat(data["last_certified"]) if data["last_certified"] else None,
            weekly_benefit_amount=data["weekly_benefit_amount"],
            remaining_balance=data["remaining_balance"],
            pending_issues=data["pending_issues"],
            next_payment_date=datetime.fromisoformat(data["next_payment_date"]) if data["next_payment_date"] else None,
        )

    def get_eligibility(self, claim_type: str) -> EligibilityAssessment:
        rules = ELIGIBILITY_RULES.get(claim_type, ELIGIBILITY_RULES["UI"])
        return EligibilityAssessment(
            claim_type=rules["claim_type"],
            likely_eligible=rules["likely_eligible"],
            confidence=rules["confidence"],
            factors=rules["factors"],
            requirements=rules["requirements"],
            next_steps=rules["next_steps"],
        )

    def get_document_checklist(self, claim_type: str) -> list[DocumentItem]:
        items = DOCUMENT_CHECKLISTS.get(claim_type, DOCUMENT_CHECKLISTS["UI"])
        return [
            DocumentItem(
                name=item["name"],
                required=item["required"],
                submitted=item["submitted"],
                description=item["description"],
            )
            for item in items
        ]

    def get_filing_steps(self, claim_type: str) -> list[str]:
        return FILING_STEPS.get(claim_type, FILING_STEPS["UI"])

    def verify_identity(self, last_four_ssn: str, date_of_birth: str) -> IdentityVerification:
        return IdentityVerification(
            last_four_ssn=last_four_ssn,
            date_of_birth=date_of_birth,
            verified=True,
        )

    def get_policy_articles(self, claim_type: str | None = None) -> list[PolicyArticle]:
        results = []
        for article in POLICY_ARTICLES_DB:
            if claim_type and claim_type not in article["claim_types"]:
                continue
            results.append(
                PolicyArticle(
                    article_id=article["article_id"],
                    title=article["title"],
                    content=article["content"],
                    claim_types=article["claim_types"],
                    last_updated=datetime.fromisoformat(article["last_updated"]),
                )
            )
        return results
