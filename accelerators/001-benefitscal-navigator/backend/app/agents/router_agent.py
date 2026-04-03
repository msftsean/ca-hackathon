"""RouterAgent — Routes queries to the appropriate program knowledge base."""

from app.models.schemas import BenefitQuery


class RouterAgent:
    """Routes benefit queries to CalFresh, CalWORKs, Medi-Cal, or general CDSS knowledge."""

    PROGRAM_MAP = {
        "calfresh": "calfresh",
        "snap": "calfresh",
        "food stamps": "calfresh",
        "calworks": "calworks",
        "cash aid": "calworks",
        "medi-cal": "medi-cal",
        "medicaid": "medi-cal",
    }

    async def route(self, query: BenefitQuery) -> str:
        if query.program:
            return query.program
        for keyword, program in self.PROGRAM_MAP.items():
            if keyword in query.raw_input.lower():
                return program
        return "general"
