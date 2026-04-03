"""QueryAgent — Detects language, extracts intent, filters PII."""

import re

from app.models.schemas import EmergencyQuery


class QueryAgent:
    """First stage: parses user input into a structured EmergencyQuery."""

    INTENT_KEYWORDS: dict[str, list[str]] = {
        "active_alerts": ["alert", "warning", "danger", "emergency", "notification", "update"],
        "evacuation_status": ["evacuate", "evacuation", "leave", "flee", "escape", "order"],
        "shelter_search": ["shelter", "refuge", "safe place", "housing", "stay", "sleep"],
        "air_quality": ["air", "aqi", "smoke", "breathing", "pollution", "quality"],
        "safety_tips": ["prepare", "kit", "safety", "protect", "ready", "plan"],
        "general_info": ["help", "info", "information", "what", "how", "where"],
    }

    EMERGENCY_TYPES: dict[str, list[str]] = {
        "wildfire": ["fire", "wildfire", "burn", "blaze", "flames"],
        "earthquake": ["earthquake", "quake", "tremor", "seismic", "shaking"],
        "flood": ["flood", "flooding", "water", "rain", "storm", "surge"],
        "tsunami": ["tsunami", "wave", "coastal"],
        "hazmat": ["hazmat", "chemical", "spill", "toxic", "hazardous"],
    }

    PII_PATTERNS = [r"\b\d{3}-\d{2}-\d{4}\b", r"\b\d{9}\b"]

    async def process(self, user_input: str, language: str = "en") -> EmergencyQuery:
        lower = user_input.lower()
        intent = self._detect_intent(lower)
        emergency_type = self._detect_emergency_type(lower)
        location = self._extract_location(user_input)
        has_pii = self._check_pii(user_input)

        entities: dict = {"has_pii": has_pii}
        if location:
            entities["location"] = location

        return EmergencyQuery(
            raw_input=user_input if not has_pii else "[PII REDACTED]",
            intent=intent,
            language=language,
            location=location,
            emergency_type=emergency_type,
            entities=entities,
        )

    def _detect_intent(self, text: str) -> str:
        scores: dict[str, int] = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            scores[intent] = sum(1 for k in keywords if k in text)
        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        return best if scores[best] > 0 else "general_info"

    def _detect_emergency_type(self, text: str) -> str | None:
        for etype, keywords in self.EMERGENCY_TYPES.items():
            if any(k in text for k in keywords):
                return etype
        return None

    def _extract_location(self, text: str) -> str | None:
        zip_match = re.search(r"\b(9\d{4})\b", text)
        if zip_match:
            return zip_match.group(1)
        return None

    def _check_pii(self, text: str) -> bool:
        return any(re.search(p, text) for p in self.PII_PATTERNS)
