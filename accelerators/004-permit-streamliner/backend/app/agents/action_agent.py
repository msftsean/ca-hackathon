"""ActionAgent — Generates checklists, validates documents, and tracks SLAs."""

import os
from app.models.schemas import PermitQuery, PermitApplication
from app.services.mock_service import MockPermitService


class ActionAgent:
    """Processes permit applications and generates requirement checklists."""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockPermitService()

    async def execute(self, query: PermitQuery, jurisdiction: str) -> PermitApplication:
        if self.mock_mode:
            return self.mock_service.get_permit_status(query, jurisdiction)
        raise NotImplementedError("Live services not yet configured")
