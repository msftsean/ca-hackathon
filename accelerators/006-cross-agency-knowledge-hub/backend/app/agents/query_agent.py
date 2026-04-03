"""QueryAgent — Parses knowledge search queries and detects scope."""

from app.models.schemas import KnowledgeQuery


class QueryAgent:
    """Detects search intent, topic, and agency scope from user queries."""

    async def process(self, user_input: str, user_agency: str | None = None) -> KnowledgeQuery:
        return KnowledgeQuery(
            raw_input=user_input,
            intent="search",
            topic=None,
            agency_scope=user_agency or "all",
            search_mode="hybrid",
        )
