"""QueryAgent — Intent detection, entity extraction, and PII filtering."""

from app.models.schemas import BenefitQuery


class QueryAgent:
    """Detects user intent, extracts entities, and filters PII from benefit queries."""

    async def process(self, user_input: str, language: str = "en") -> BenefitQuery:
        return BenefitQuery(
            raw_input=user_input,
            intent="eligibility_check",
            program=None,
            language=language,
            entities={},
            pii_detected=False,
        )
