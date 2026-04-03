"""QueryAgent — Parses incident reports and situation queries."""

from app.models.schemas import IncidentQuery


class QueryAgent:
    """Detects query intent for wildfire incident reports and resource requests."""

    async def process(self, user_input: str) -> IncidentQuery:
        return IncidentQuery(
            raw_input=user_input,
            intent="situation_report",
            incident_id=None,
            region=None,
            entities={},
        )
