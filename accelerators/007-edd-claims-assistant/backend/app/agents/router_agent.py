"""RouterAgent — Routes to UI, DI, or PFL claim processing."""

from app.models.schemas import ClaimQuery


class RouterAgent:
    """Routes claim queries to the appropriate EDD program module."""

    PROGRAM_MAP = {
        "unemployment": "ui",
        "laid off": "ui",
        "lost job": "ui",
        "disability": "di",
        "injured": "di",
        "medical": "di",
        "family leave": "pfl",
        "parental": "pfl",
        "bonding": "pfl",
    }

    async def route(self, query: ClaimQuery) -> str:
        if query.program:
            return query.program
        for keyword, program in self.PROGRAM_MAP.items():
            if keyword in query.raw_input.lower():
                return program
        return "ui"
