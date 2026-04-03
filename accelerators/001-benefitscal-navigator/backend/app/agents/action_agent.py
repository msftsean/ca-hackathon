"""ActionAgent — Retrieves knowledge and generates citation-backed responses."""

import os
from app.models.schemas import BenefitQuery, EligibilityResult
from app.services.mock_service import MockBenefitsService


class ActionAgent:
    """Generates responses using RAG over CDSS program knowledge bases."""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockBenefitsService()

    async def execute(self, query: BenefitQuery, program: str) -> EligibilityResult:
        if self.mock_mode:
            return self.mock_service.get_eligibility_info(query, program)
        raise NotImplementedError("Live Azure services not yet configured")
