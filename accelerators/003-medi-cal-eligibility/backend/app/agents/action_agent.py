"""ActionAgent — Performs eligibility determination using extracted income data."""

import os
from app.models.schemas import EligibilityQuery, EligibilityDetermination
from app.services.mock_service import MockMediCalService


class ActionAgent:
    """Runs MAGI eligibility rules against extracted document data."""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockMediCalService()

    async def execute(self, query: EligibilityQuery, pathway: str) -> EligibilityDetermination:
        if self.mock_mode:
            return self.mock_service.determine_eligibility(query)
        raise NotImplementedError("Live Azure services not yet configured")
