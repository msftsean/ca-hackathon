"""RouterAgent — Routes to alert, shelter, or safety knowledge bases."""

from app.models.schemas import EmergencyQuery


class RouterAgent:
    """Routes emergency queries to the appropriate information source."""

    async def route(self, query: EmergencyQuery) -> str:
        intent_map = {
            "active_alerts": "alerts",
            "shelter_info": "shelters",
            "safety_instructions": "safety",
            "general_info": "general",
        }
        return intent_map.get(query.intent, "general")
