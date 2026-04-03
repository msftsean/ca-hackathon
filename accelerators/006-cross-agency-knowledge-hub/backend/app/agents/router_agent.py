"""RouterAgent — Routes queries to appropriate agency knowledge bases."""

from app.models.schemas import KnowledgeQuery


class RouterAgent:
    """Routes search queries to one or more agency knowledge bases."""

    AGENCY_INDICES = {
        "cdt": "index-cdt-policies",
        "dgs": "index-dgs-procurement",
        "calhr": "index-calhr-hr",
        "govops": "index-govops-general",
        "all": "index-federated",
    }

    async def route(self, query: KnowledgeQuery) -> list[str]:
        scope = query.agency_scope or "all"
        if scope == "all":
            return list(self.AGENCY_INDICES.values())
        return [self.AGENCY_INDICES.get(scope, "index-federated")]
