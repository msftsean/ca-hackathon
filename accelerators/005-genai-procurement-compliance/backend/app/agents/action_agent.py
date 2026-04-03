"""ActionAgent — Evaluates vendor compliance and generates scores."""

import os
from app.models.schemas import ComplianceQuery, ComplianceReport
from app.services.mock_service import MockComplianceService


class ActionAgent:
    """Scores vendor attestations against compliance frameworks."""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockComplianceService()

    async def execute(self, query: ComplianceQuery, frameworks: list[str]) -> ComplianceReport:
        if self.mock_mode:
            return self.mock_service.evaluate_compliance(query, frameworks)
        raise NotImplementedError("Live Azure services not yet configured")
