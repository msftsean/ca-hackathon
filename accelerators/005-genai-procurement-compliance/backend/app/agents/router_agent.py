"""RouterAgent — Routes to the appropriate compliance framework evaluation."""

from app.models.schemas import ComplianceQuery


class RouterAgent:
    """Routes attestation reviews to relevant compliance framework evaluators."""

    async def route(self, query: ComplianceQuery) -> list[str]:
        frameworks = query.frameworks or []
        if not frameworks:
            frameworks = ["eo-n-5-26", "sb-53", "simm-5300"]
        return frameworks
