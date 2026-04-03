"""ActionAgent — Performs hybrid search and synthesizes results."""

import os
from app.models.schemas import KnowledgeQuery, SearchResult
from app.services.mock_service import MockKnowledgeService


class ActionAgent:
    """Executes hybrid BM25 + semantic search across agency knowledge bases."""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockKnowledgeService()

    async def execute(self, query: KnowledgeQuery, indices: list[str]) -> list[SearchResult]:
        if self.mock_mode:
            return self.mock_service.search(query)
        raise NotImplementedError("Live Azure services not yet configured")
