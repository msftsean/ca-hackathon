"""ActionAgent — Retrieves claim status and performs eligibility screening."""

import os
from app.models.schemas import ClaimQuery, ClaimStatus
from app.services.mock_service import MockEDDService


class ActionAgent:
    """Processes claim status checks, eligibility screening, and ticket creation."""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockEDDService()

    async def execute(self, query: ClaimQuery, program: str) -> ClaimStatus:
        if self.mock_mode:
            return self.mock_service.get_claim_status(query, program)
        raise NotImplementedError("Live EDD services not yet configured")
