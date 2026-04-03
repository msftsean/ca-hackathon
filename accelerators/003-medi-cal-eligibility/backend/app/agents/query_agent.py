"""QueryAgent — Document intake and eligibility query parsing."""

from app.models.schemas import EligibilityQuery


class QueryAgent:
    """Parses eligibility queries and processes document uploads."""

    async def process(self, user_input: str, document_ids: list[str] | None = None) -> EligibilityQuery:
        return EligibilityQuery(
            raw_input=user_input,
            intent="eligibility_check",
            document_ids=document_ids or [],
            applicant_info={},
            pii_detected=False,
        )
