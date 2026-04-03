"""RouterAgent — Routes to MAGI or non-MAGI eligibility pathways."""

from app.models.schemas import EligibilityQuery


class RouterAgent:
    """Routes eligibility queries to the appropriate determination pathway."""

    async def route(self, query: EligibilityQuery) -> str:
        if query.intent == "document_upload":
            return "document_extraction"
        if query.intent == "status_check":
            return "application_status"
        return "magi_determination"
