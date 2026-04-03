"""QueryAgent — Intent detection and entity extraction for wildfire incidents."""

import re
from app.models.schemas import IncidentQuery


class QueryAgent:
    """Detects user intent and extracts entities from wildfire/emergency queries."""

    INTENT_KEYWORDS: dict[str, list[str]] = {
        "incident_report": ["fire", "incident", "report", "new fire", "smoke", "burning", "blaze"],
        "evacuation_query": ["evacuate", "evacuation", "zone", "leave", "order", "shelter", "flee"],
        "agency_coordination": ["coordinate", "mutual aid", "agency", "contact", "interagency"],
        "resource_request": ["resources", "engine", "crew", "helicopter", "need", "send", "deploy", "dozer", "tanker"],
        "weather_check": ["weather", "wind", "humidity", "red flag", "fire weather", "temperature", "forecast"],
        "psps_info": ["power", "shutoff", "psps", "utility", "outage", "electricity", "pge", "sce"],
        "status_update": ["status", "update", "containment", "progress", "contained", "controlled"],
    }

    INCIDENT_TYPES = {
        "wildfire": ["wildfire", "wild fire", "brush fire", "forest fire"],
        "structure_fire": ["structure fire", "building fire", "house fire"],
        "flood": ["flood", "flooding", "flash flood"],
        "earthquake": ["earthquake", "quake", "seismic"],
        "hazmat": ["hazmat", "hazardous material", "chemical spill", "toxic"],
    }

    RESOURCE_TYPES = ["engine", "crew", "helicopter", "dozer", "water tender", "air tanker"]

    AGENCY_NAMES = ["cal fire", "cal oes", "cdf", "chp", "usfs", "nws", "county fire"]

    CALIFORNIA_COUNTIES = [
        "butte", "los angeles", "sacramento", "san diego", "san francisco",
        "orange", "riverside", "san bernardino", "ventura", "santa barbara",
        "sonoma", "napa", "lake", "mendocino", "shasta",
    ]

    async def process(self, user_input: str) -> IncidentQuery:
        """Parse user input to detect intent and extract entities."""
        lower_input = user_input.lower()
        intent = self._detect_intent(lower_input)
        entities = self._extract_entities(lower_input)
        incident_type = self._detect_incident_type(lower_input)

        return IncidentQuery(
            raw_input=user_input,
            intent=intent,
            entities=entities,
            incident_type=incident_type,
        )

    def _detect_intent(self, text: str) -> str:
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return intent
        return "general_info"

    def _extract_entities(self, text: str) -> dict:
        entities: dict = {}

        # Extract location/county
        for county in self.CALIFORNIA_COUNTIES:
            if county in text:
                entities["county"] = county.title()
                break

        # Extract resource types
        found_resources = [r for r in self.RESOURCE_TYPES if r in text]
        if found_resources:
            entities["resource_types"] = found_resources

        # Extract agency names
        found_agencies = [a for a in self.AGENCY_NAMES if a in text]
        if found_agencies:
            entities["agencies"] = found_agencies

        # Extract incident IDs (CA-XXX-XXXXXX pattern)
        id_match = re.search(r"CA-[A-Z]{2,4}-\d{3,6}", text, re.IGNORECASE)
        if id_match:
            entities["incident_id"] = id_match.group(0).upper()

        # Extract acreage
        acre_match = re.search(r"(\d[\d,]*)\s*acres?", text)
        if acre_match:
            entities["acres"] = float(acre_match.group(1).replace(",", ""))

        # Extract containment percentage
        contain_match = re.search(r"(\d+)\s*%?\s*contain", text)
        if contain_match:
            entities["containment_pct"] = float(contain_match.group(1))

        return entities

    def _detect_incident_type(self, text: str) -> str | None:
        for itype, keywords in self.INCIDENT_TYPES.items():
            for kw in keywords:
                if kw in text:
                    return itype
        return None
