"""Mock service returning sample knowledge search results."""

from datetime import datetime
from app.models.schemas import KnowledgeQuery, SearchResult


class MockKnowledgeService:
    """Returns mock search results across agency knowledge bases."""

    def search(self, query: KnowledgeQuery) -> list[SearchResult]:
        return [
            SearchResult(
                document_id="POL-CDT-2024-001",
                title="Statewide AI Use Policy — CDT",
                snippet="All state agencies must complete an AI impact assessment prior to deploying generative AI solutions in production environments...",
                source_agency="CDT",
                document_type="policy",
                url="https://cdt.ca.gov/policies/ai-use",
                relevance_score=0.94,
                last_updated=datetime(2024, 6, 15),
            ),
            SearchResult(
                document_id="PROC-DGS-2024-042",
                title="IT Procurement Guidelines — DGS",
                snippet="Vendors providing AI services to the state must submit attestation forms per EO N-5-26 requirements...",
                source_agency="DGS",
                document_type="procedure",
                url="https://dgs.ca.gov/procurement/it-guidelines",
                relevance_score=0.87,
                last_updated=datetime(2024, 9, 1),
            ),
            SearchResult(
                document_id="MEMO-GOVOPS-2024-007",
                title="Cross-Agency Data Sharing Framework",
                snippet="Agencies may share de-identified data for research and operational improvement under the following conditions...",
                source_agency="GovOps",
                document_type="memo",
                url="https://govops.ca.gov/data-sharing",
                relevance_score=0.79,
                last_updated=datetime(2024, 11, 20),
            ),
        ]
