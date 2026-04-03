"""ActionAgent — Generates tactical response recommendations."""

import os
from app.models.schemas import IncidentQuery, WildfireIncident
from app.services.mock_service import MockWildfireService


class ActionAgent:
    """Generates actionable intelligence for wildfire response."""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockWildfireService()

    async def execute(self, query: IncidentQuery, module: str) -> list[WildfireIncident]:
        if self.mock_mode:
            return self.mock_service.get_incidents()
        raise NotImplementedError("Live services not yet configured")
