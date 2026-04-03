"""RouterAgent — Routes to the correct jurisdiction and permit pathway."""

from app.models.schemas import PermitQuery


class RouterAgent:
    """Routes permit queries to the appropriate agency and processing pathway."""

    JURISDICTION_MAP = {
        "housing": "hcd",
        "residential": "hcd",
        "adu": "hcd",
        "commercial": "opr",
        "environmental": "opr",
        "ceqa": "opr",
        "contractor": "dca",
        "license": "dca",
        "professional": "dca",
    }

    async def route(self, query: PermitQuery) -> str:
        if query.jurisdiction:
            return query.jurisdiction
        for keyword, agency in self.JURISDICTION_MAP.items():
            if keyword in query.raw_input.lower():
                return agency
        return "opr"
