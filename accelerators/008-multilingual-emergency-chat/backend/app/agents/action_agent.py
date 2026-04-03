"""ActionAgent — Retrieves emergency info and translates responses."""

import os
from app.models.schemas import EmergencyQuery, EmergencyAlert
from app.services.mock_service import MockEmergencyService


class ActionAgent:
    """Retrieves emergency information and delivers translated responses."""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockEmergencyService()

    async def execute(self, query: EmergencyQuery, source: str) -> list[EmergencyAlert]:
        if self.mock_mode:
            return self.mock_service.get_alerts(query)
        raise NotImplementedError("Live services not yet configured")
