"""QueryAgent — Detects language and parses emergency queries."""

from app.models.schemas import EmergencyQuery


class QueryAgent:
    """Detects user language and extracts emergency query intent."""

    async def process(self, user_input: str, detected_language: str = "en") -> EmergencyQuery:
        intent = "general_info"
        if any(w in user_input.lower() for w in ["shelter", "evacuate", "evacuation", "refuge"]):
            intent = "shelter_info"
        elif any(w in user_input.lower() for w in ["alert", "warning", "danger", "emergency"]):
            intent = "active_alerts"
        elif any(w in user_input.lower() for w in ["safe", "safety", "prepare", "kit"]):
            intent = "safety_instructions"

        return EmergencyQuery(
            raw_input=user_input,
            intent=intent,
            language=detected_language,
            location=None,
            emergency_type=None,
        )
