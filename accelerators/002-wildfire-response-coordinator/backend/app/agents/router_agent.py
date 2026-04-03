"""RouterAgent — Routes to incident management, resources, or evacuation modules."""

from app.models.schemas import IncidentQuery


class RouterAgent:
    """Routes wildfire queries to appropriate response modules."""

    async def route(self, query: IncidentQuery) -> str:
        intent_map = {
            "situation_report": "incident_management",
            "resource_request": "resource_allocation",
            "evacuation": "evacuation_routing",
            "weather": "weather_intelligence",
        }
        return intent_map.get(query.intent, "incident_management")
