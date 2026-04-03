"""QueryAgent — Parses permit applications and status queries."""

from app.models.schemas import PermitQuery


class QueryAgent:
    """Detects intent from permit-related queries and extracts application details."""

    async def process(self, user_input: str) -> PermitQuery:
        return PermitQuery(
            raw_input=user_input,
            intent="permit_inquiry",
            permit_type=None,
            jurisdiction=None,
            entities={},
        )
