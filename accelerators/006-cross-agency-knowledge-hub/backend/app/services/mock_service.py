"""Mock service returning sample knowledge search results."""

from datetime import datetime
from app.models.schemas import (
    AgencyPermission,
    CrossReference,
    DocumentResult,
    ExpertInfo,
)


DOCUMENTS_DB: list[dict] = [
    {
        "doc_id": "POL-CDSS-2024-001",
        "title": "CalFresh Program Policy Manual",
        "agency": "CDSS",
        "department": "CalFresh Division",
        "document_type": "policy",
        "summary": "Comprehensive policy guidelines for CalFresh program eligibility, application processing, and benefit issuance across California counties.",
        "relevance_score": 0.95,
        "last_updated": "2024-06-15T00:00:00",
        "access_level": "public",
        "keywords": ["calfresh", "food", "snap", "eligibility", "benefits", "nutrition"],
    },
    {
        "doc_id": "POL-CDSS-2024-002",
        "title": "CalWORKs Welfare-to-Work Requirements",
        "agency": "CDSS",
        "department": "CalWORKs Division",
        "document_type": "policy",
        "summary": "Policy on welfare-to-work program participation requirements, exemptions, and sanctions for CalWORKs recipients.",
        "relevance_score": 0.90,
        "last_updated": "2024-03-01T00:00:00",
        "access_level": "public",
        "keywords": ["calworks", "welfare", "work", "employment", "cash", "aid"],
    },
    {
        "doc_id": "PROC-CalHR-2024-001",
        "title": "State Employee Classification Procedures",
        "agency": "CalHR",
        "department": "Classification Services",
        "document_type": "procedure",
        "summary": "Procedures for classifying state employee positions, including IT classifications, management positions, and specialized roles.",
        "relevance_score": 0.88,
        "last_updated": "2024-08-20T00:00:00",
        "access_level": "internal",
        "keywords": ["classification", "employee", "position", "hr", "human", "resources", "staff"],
    },
    {
        "doc_id": "REG-CalHR-2024-002",
        "title": "Telework Policy for State Agencies",
        "agency": "CalHR",
        "department": "Policy Division",
        "document_type": "regulation",
        "summary": "Statewide regulations governing telework eligibility, schedules, and performance expectations for California state employees.",
        "relevance_score": 0.85,
        "last_updated": "2024-09-15T00:00:00",
        "access_level": "public",
        "keywords": ["telework", "remote", "work", "employee", "policy", "schedule"],
    },
    {
        "doc_id": "POL-Caltrans-2024-001",
        "title": "Highway Maintenance Standards Manual",
        "agency": "Caltrans",
        "department": "Maintenance Division",
        "document_type": "policy",
        "summary": "Standards and procedures for California state highway maintenance, including pavement repair, signage, and vegetation management.",
        "relevance_score": 0.82,
        "last_updated": "2024-01-10T00:00:00",
        "access_level": "public",
        "keywords": ["highway", "maintenance", "road", "pavement", "transportation", "infrastructure"],
    },
    {
        "doc_id": "GUID-Caltrans-2024-002",
        "title": "Environmental Review Guidance for Transportation Projects",
        "agency": "Caltrans",
        "department": "Environmental Division",
        "document_type": "guidance",
        "summary": "Guidance for conducting environmental reviews under CEQA and NEPA for transportation infrastructure projects.",
        "relevance_score": 0.80,
        "last_updated": "2024-07-01T00:00:00",
        "access_level": "public",
        "keywords": ["environmental", "ceqa", "nepa", "review", "transportation", "project"],
    },
    {
        "doc_id": "POL-DHCS-2024-001",
        "title": "Medi-Cal Managed Care Policy Guide",
        "agency": "DHCS",
        "department": "Managed Care Division",
        "document_type": "policy",
        "summary": "Policy guide for Medi-Cal managed care plans, including enrollment, provider networks, and quality standards.",
        "relevance_score": 0.93,
        "last_updated": "2024-05-20T00:00:00",
        "access_level": "public",
        "keywords": ["medi-cal", "managed", "care", "health", "enrollment", "provider"],
    },
    {
        "doc_id": "FAQ-DHCS-2024-002",
        "title": "Medi-Cal Eligibility FAQ",
        "agency": "DHCS",
        "department": "Eligibility Division",
        "document_type": "faq",
        "summary": "Frequently asked questions about Medi-Cal eligibility requirements, application process, and coverage details.",
        "relevance_score": 0.87,
        "last_updated": "2024-10-01T00:00:00",
        "access_level": "public",
        "keywords": ["medi-cal", "eligibility", "faq", "health", "coverage", "application"],
    },
    {
        "doc_id": "PROC-EDD-2024-001",
        "title": "Unemployment Insurance Claims Processing Procedures",
        "agency": "EDD",
        "department": "UI Division",
        "document_type": "procedure",
        "summary": "Detailed procedures for processing unemployment insurance claims, including initial filing, certification, and appeals.",
        "relevance_score": 0.91,
        "last_updated": "2024-04-15T00:00:00",
        "access_level": "internal",
        "keywords": ["unemployment", "claims", "ui", "insurance", "filing", "edd", "certification"],
    },
    {
        "doc_id": "MEMO-EDD-2024-002",
        "title": "EDD Data Governance Memorandum",
        "agency": "EDD",
        "department": "IT Division",
        "document_type": "memo",
        "summary": "Memorandum establishing data governance standards for EDD systems, covering data quality, access controls, and retention policies.",
        "relevance_score": 0.78,
        "last_updated": "2024-11-01T00:00:00",
        "access_level": "internal",
        "keywords": ["data", "governance", "edd", "quality", "access", "retention", "security"],
    },
    {
        "doc_id": "POL-CDSS-2024-003",
        "title": "Data Sharing and Privacy Policy",
        "agency": "CDSS",
        "department": "Privacy Office",
        "document_type": "policy",
        "summary": "Policy governing data sharing between CDSS and other state agencies, including CCPA/CPRA compliance requirements.",
        "relevance_score": 0.86,
        "last_updated": "2024-08-01T00:00:00",
        "access_level": "public",
        "keywords": ["data", "sharing", "privacy", "ccpa", "cpra", "governance", "compliance"],
    },
    {
        "doc_id": "GUID-DHCS-2024-003",
        "title": "Telehealth Services Guidance",
        "agency": "DHCS",
        "department": "Benefits Division",
        "document_type": "guidance",
        "summary": "Guidance for Medi-Cal providers on delivering telehealth services, including billing codes and documentation requirements.",
        "relevance_score": 0.83,
        "last_updated": "2024-09-10T00:00:00",
        "access_level": "public",
        "keywords": ["telehealth", "medi-cal", "provider", "billing", "health", "remote"],
    },
]


CROSS_REFERENCES_DB: list[dict] = [
    {
        "source_doc_id": "POL-CDSS-2024-003",
        "target_doc_id": "MEMO-EDD-2024-002",
        "relationship": "complements",
        "description": "CDSS data sharing policy complements EDD data governance memo on inter-agency data exchange.",
    },
    {
        "source_doc_id": "REG-CalHR-2024-002",
        "target_doc_id": "POL-CDSS-2024-002",
        "relationship": "cites",
        "description": "CalHR telework regulation cites CalWORKs welfare-to-work policy for employment requirements.",
    },
    {
        "source_doc_id": "POL-DHCS-2024-001",
        "target_doc_id": "FAQ-DHCS-2024-002",
        "relationship": "complements",
        "description": "Medi-Cal managed care policy is complemented by the eligibility FAQ.",
    },
    {
        "source_doc_id": "POL-CDSS-2024-001",
        "target_doc_id": "POL-CDSS-2024-002",
        "relationship": "complements",
        "description": "CalFresh policy complements CalWORKs policy — both serve overlapping populations.",
    },
    {
        "source_doc_id": "PROC-EDD-2024-001",
        "target_doc_id": "POL-CDSS-2024-003",
        "relationship": "cites",
        "description": "EDD claims procedures cite CDSS privacy policy for data handling requirements.",
    },
    {
        "source_doc_id": "GUID-Caltrans-2024-002",
        "target_doc_id": "POL-Caltrans-2024-001",
        "relationship": "supersedes",
        "description": "Environmental review guidance supersedes earlier maintenance standards for environmental compliance.",
    },
]


EXPERTS_DB: list[dict] = [
    {
        "expert_id": "EXP-001",
        "name": "Maria Chen",
        "agency": "CDSS",
        "department": "CalFresh Division",
        "expertise_areas": ["CalFresh", "SNAP", "nutrition assistance", "eligibility"],
        "email": "maria.chen@cdss.ca.gov",
        "available": True,
    },
    {
        "expert_id": "EXP-002",
        "name": "James Rodriguez",
        "agency": "CalHR",
        "department": "Policy Division",
        "expertise_areas": ["telework", "employee classification", "labor relations", "HR policy"],
        "email": "james.rodriguez@calhr.ca.gov",
        "available": True,
    },
    {
        "expert_id": "EXP-003",
        "name": "Sarah Kim",
        "agency": "DHCS",
        "department": "Managed Care Division",
        "expertise_areas": ["Medi-Cal", "managed care", "health policy", "provider networks"],
        "email": "sarah.kim@dhcs.ca.gov",
        "available": True,
    },
    {
        "expert_id": "EXP-004",
        "name": "Robert Taylor",
        "agency": "EDD",
        "department": "UI Division",
        "expertise_areas": ["unemployment insurance", "claims processing", "appeals", "UI policy"],
        "email": "robert.taylor@edd.ca.gov",
        "available": False,
    },
    {
        "expert_id": "EXP-005",
        "name": "Lisa Patel",
        "agency": "DGS",
        "department": "Procurement Division",
        "expertise_areas": ["procurement", "vendor management", "IT contracts", "compliance"],
        "email": "lisa.patel@dgs.ca.gov",
        "available": True,
    },
    {
        "expert_id": "EXP-006",
        "name": "David Wong",
        "agency": "Caltrans",
        "department": "Environmental Division",
        "expertise_areas": ["CEQA", "environmental review", "transportation planning"],
        "email": "david.wong@dot.ca.gov",
        "available": True,
    },
]


AGENCY_PERMISSIONS_DB: list[dict] = [
    {
        "agency_code": "CDSS",
        "agency_name": "California Department of Social Services",
        "access_level": "full",
        "departments": ["CalFresh Division", "CalWORKs Division", "Privacy Office", "Children Services"],
    },
    {
        "agency_code": "CalHR",
        "agency_name": "California Department of Human Resources",
        "access_level": "full",
        "departments": ["Classification Services", "Policy Division", "Benefits Division"],
    },
    {
        "agency_code": "Caltrans",
        "agency_name": "California Department of Transportation",
        "access_level": "full",
        "departments": ["Maintenance Division", "Environmental Division", "Planning Division"],
    },
    {
        "agency_code": "DHCS",
        "agency_name": "Department of Health Care Services",
        "access_level": "full",
        "departments": ["Managed Care Division", "Eligibility Division", "Benefits Division"],
    },
    {
        "agency_code": "EDD",
        "agency_name": "Employment Development Department",
        "access_level": "full",
        "departments": ["UI Division", "DI Division", "IT Division", "Tax Division"],
    },
]


class MockKnowledgeService:
    """Returns mock knowledge search results for development and testing."""

    def _match_score(self, doc: dict, keywords: list[str]) -> float:
        if not keywords:
            return doc.get("relevance_score", 0.5)
        doc_keywords = doc.get("keywords", [])
        doc_text = (
            doc.get("title", "").lower()
            + " "
            + doc.get("summary", "").lower()
            + " "
            + " ".join(doc_keywords)
        )
        matches = sum(1 for kw in keywords if kw.lower() in doc_text)
        base_score = doc.get("relevance_score", 0.5)
        return min(1.0, base_score + (matches * 0.05))

    def search_documents(
        self,
        keywords: list[str] | None = None,
        agencies: list[str] | None = None,
        document_types: list[str] | None = None,
    ) -> list[DocumentResult]:
        results = []
        for doc in DOCUMENTS_DB:
            if agencies and doc["agency"] not in agencies:
                continue
            if document_types and doc["document_type"] not in document_types:
                continue

            score = self._match_score(doc, keywords or [])
            results.append(
                DocumentResult(
                    doc_id=doc["doc_id"],
                    title=doc["title"],
                    agency=doc["agency"],
                    department=doc["department"],
                    document_type=doc["document_type"],
                    summary=doc["summary"],
                    relevance_score=score,
                    last_updated=datetime.fromisoformat(doc["last_updated"]),
                    access_level=doc["access_level"],
                )
            )

        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:10]

    def get_document_by_id(self, doc_id: str) -> DocumentResult | None:
        for doc in DOCUMENTS_DB:
            if doc["doc_id"] == doc_id:
                return DocumentResult(
                    doc_id=doc["doc_id"],
                    title=doc["title"],
                    agency=doc["agency"],
                    department=doc["department"],
                    document_type=doc["document_type"],
                    summary=doc["summary"],
                    relevance_score=doc["relevance_score"],
                    last_updated=datetime.fromisoformat(doc["last_updated"]),
                    access_level=doc["access_level"],
                )
        return None

    def find_experts(
        self,
        keywords: list[str] | None = None,
        agencies: list[str] | None = None,
    ) -> list[ExpertInfo]:
        results = []
        for exp in EXPERTS_DB:
            if agencies and exp["agency"] not in agencies:
                continue
            if keywords:
                exp_text = " ".join(exp["expertise_areas"]).lower() + " " + exp["department"].lower()
                if not any(kw.lower() in exp_text for kw in keywords):
                    continue
            results.append(
                ExpertInfo(
                    expert_id=exp["expert_id"],
                    name=exp["name"],
                    agency=exp["agency"],
                    department=exp["department"],
                    expertise_areas=exp["expertise_areas"],
                    email=exp["email"],
                    available=exp["available"],
                )
            )
        return results

    def get_cross_references(
        self,
        keywords: list[str] | None = None,
        agencies: list[str] | None = None,
    ) -> list[CrossReference]:
        results = []
        for ref in CROSS_REFERENCES_DB:
            if keywords:
                ref_text = ref["description"].lower()
                if not any(kw.lower() in ref_text for kw in keywords):
                    continue
            if agencies:
                source_agency = None
                target_agency = None
                for doc in DOCUMENTS_DB:
                    if doc["doc_id"] == ref["source_doc_id"]:
                        source_agency = doc["agency"]
                    if doc["doc_id"] == ref["target_doc_id"]:
                        target_agency = doc["agency"]
                if source_agency and source_agency not in agencies:
                    if target_agency and target_agency not in agencies:
                        continue
            results.append(
                CrossReference(
                    source_doc_id=ref["source_doc_id"],
                    target_doc_id=ref["target_doc_id"],
                    relationship=ref["relationship"],
                    description=ref["description"],
                )
            )
        return results

    def get_agency_permissions(self) -> list[AgencyPermission]:
        return [
            AgencyPermission(
                agency_code=a["agency_code"],
                agency_name=a["agency_name"],
                access_level=a["access_level"],
                departments=a["departments"],
            )
            for a in AGENCY_PERMISSIONS_DB
        ]
