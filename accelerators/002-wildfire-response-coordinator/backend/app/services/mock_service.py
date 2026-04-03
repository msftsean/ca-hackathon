"""Mock service returning sample wildfire incident data."""

from datetime import datetime, timedelta
from app.models.schemas import (
    Incident, ResourceAllocation, EvacuationZone, EvacuationInfo,
    WeatherCondition, PSPSEvent, AgencyAssignment,
)


class MockWildfireService:
    """Returns mock wildfire data for development and testing."""

    INCIDENTS: dict[str, Incident] = {
        "CA-BTU-004521": Incident(
            incident_id="CA-BTU-004521", name="Paradise Ridge Fire",
            incident_type="wildfire", severity="major",
            location="Paradise Ridge, Butte County", county="Butte",
            acres_burned=12500.0, containment_pct=35.0,
            lead_agency="CAL FIRE", status="active", mutual_aid_region=3,
            created_at=datetime(2025, 7, 10, 8, 0),
            updated_at=datetime(2025, 7, 15, 16, 0),
        ),
        "CA-LAC-008932": Incident(
            incident_id="CA-LAC-008932", name="Topanga Canyon Fire",
            incident_type="structure_fire", severity="moderate",
            location="Topanga Canyon, Los Angeles", county="Los Angeles",
            acres_burned=450.0, containment_pct=65.0,
            lead_agency="LA County FD", status="active", mutual_aid_region=1,
            created_at=datetime(2025, 7, 12, 14, 30),
            updated_at=datetime(2025, 7, 15, 12, 0),
        ),
        "CA-SAC-001122": Incident(
            incident_id="CA-SAC-001122", name="American River Flood",
            incident_type="flood", severity="minor",
            location="American River Parkway, Sacramento", county="Sacramento",
            acres_burned=0.0, containment_pct=0.0,
            lead_agency="Sacramento County OES", status="active", mutual_aid_region=4,
            created_at=datetime(2025, 7, 14, 6, 0),
            updated_at=datetime(2025, 7, 15, 10, 0),
        ),
    }

    RESOURCES: list[ResourceAllocation] = [
        ResourceAllocation(resource_id="ENG-001", resource_type="engine", quantity=3, agency="CAL FIRE", status="deployed", mutual_aid_region=3),
        ResourceAllocation(resource_id="ENG-002", resource_type="engine", quantity=2, agency="CAL FIRE", status="available", mutual_aid_region=3),
        ResourceAllocation(resource_id="ENG-003", resource_type="engine", quantity=4, agency="LA County FD", status="deployed", mutual_aid_region=1),
        ResourceAllocation(resource_id="ENG-004", resource_type="engine", quantity=2, agency="Sacramento FD", status="available", mutual_aid_region=4),
        ResourceAllocation(resource_id="CRW-001", resource_type="crew", quantity=2, agency="CAL FIRE", status="deployed", mutual_aid_region=3),
        ResourceAllocation(resource_id="CRW-002", resource_type="crew", quantity=1, agency="USFS", status="available", eta_minutes=45, mutual_aid_region=3),
        ResourceAllocation(resource_id="CRW-003", resource_type="crew", quantity=3, agency="CAL FIRE", status="en_route", eta_minutes=120, mutual_aid_region=1),
        ResourceAllocation(resource_id="HEL-001", resource_type="helicopter", quantity=1, agency="CAL FIRE", status="deployed", mutual_aid_region=3),
        ResourceAllocation(resource_id="HEL-002", resource_type="helicopter", quantity=1, agency="LA County FD", status="available", mutual_aid_region=1),
        ResourceAllocation(resource_id="HEL-003", resource_type="helicopter", quantity=1, agency="CHP", status="committed", mutual_aid_region=5),
        ResourceAllocation(resource_id="DOZ-001", resource_type="dozer", quantity=2, agency="CAL FIRE", status="deployed", mutual_aid_region=3),
        ResourceAllocation(resource_id="DOZ-002", resource_type="dozer", quantity=1, agency="USFS", status="available", mutual_aid_region=3),
        ResourceAllocation(resource_id="WT-001", resource_type="water_tender", quantity=3, agency="CAL FIRE", status="deployed", mutual_aid_region=3),
        ResourceAllocation(resource_id="WT-002", resource_type="water_tender", quantity=2, agency="CAL FIRE", status="available", mutual_aid_region=1),
        ResourceAllocation(resource_id="AT-001", resource_type="air_tanker", quantity=1, agency="CAL FIRE", status="deployed", mutual_aid_region=3),
        ResourceAllocation(resource_id="AT-002", resource_type="air_tanker", quantity=1, agency="USFS", status="available", eta_minutes=90, mutual_aid_region=5),
        ResourceAllocation(resource_id="ENG-005", resource_type="engine", quantity=2, agency="USFS", status="available", mutual_aid_region=5),
        ResourceAllocation(resource_id="ENG-006", resource_type="engine", quantity=3, agency="San Diego FD", status="available", mutual_aid_region=6),
        ResourceAllocation(resource_id="CRW-004", resource_type="crew", quantity=2, agency="CAL FIRE", status="available", mutual_aid_region=2),
        ResourceAllocation(resource_id="ENG-007", resource_type="engine", quantity=1, agency="Fresno FD", status="available", mutual_aid_region=5),
    ]

    EVACUATION_ZONES: list[EvacuationZone] = [
        EvacuationZone(
            zone_id="EZ-BTU-001", zone_name="Paradise Ridge East",
            status="order", population=4500,
            routes=["Skyway to Hwy 99", "Clark Rd to Hwy 32"],
            shelters=["Chico Fairgrounds", "Oroville Community Center"],
        ),
        EvacuationZone(
            zone_id="EZ-BTU-002", zone_name="Magalia",
            status="warning", population=8200,
            routes=["Skyway to Hwy 99 via Pentz Rd"],
            shelters=["Chico Fairgrounds"],
        ),
        EvacuationZone(
            zone_id="EZ-LAC-001", zone_name="Topanga Canyon",
            status="order", population=3100,
            routes=["Topanga Canyon Blvd to PCH", "Old Topanga Canyon Rd to Mulholland"],
            shelters=["Malibu Community Center", "Santa Monica Civic Auditorium"],
        ),
        EvacuationZone(
            zone_id="EZ-SAC-001", zone_name="River Park",
            status="shelter_in_place", population=1200,
            routes=["Garden Hwy to I-5"],
            shelters=["Cal Expo Center"],
        ),
    ]

    WEATHER: list[WeatherCondition] = [
        WeatherCondition(
            location="Butte County", temperature_f=98.0, humidity_pct=12.0,
            wind_speed_mph=25.0, wind_direction="NE",
            red_flag_warning=True, fire_weather_watch=False,
            forecast_summary="Extreme fire weather conditions. Hot, dry NE winds 20-30 mph with gusts to 45 mph through Thursday.",
        ),
        WeatherCondition(
            location="Los Angeles County", temperature_f=92.0, humidity_pct=18.0,
            wind_speed_mph=15.0, wind_direction="NW",
            red_flag_warning=False, fire_weather_watch=True,
            forecast_summary="Elevated fire weather risk. Warm and dry with moderate offshore winds expected.",
        ),
        WeatherCondition(
            location="Sacramento County", temperature_f=78.0, humidity_pct=65.0,
            wind_speed_mph=8.0, wind_direction="SW",
            red_flag_warning=False, fire_weather_watch=False,
            forecast_summary="Mild conditions with some cloudiness. Low fire risk. Continued flood watch along the American River.",
        ),
    ]

    PSPS_EVENTS: list[PSPSEvent] = [
        PSPSEvent(
            event_id="PSPS-PGE-2025-042", utility="PGE",
            status="active", affected_customers=45000,
            start_time=datetime(2025, 7, 14, 18, 0),
            estimated_restoration=datetime(2025, 7, 16, 12, 0),
            affected_areas=["Butte County", "Plumas County", "Shasta County"],
        ),
        PSPSEvent(
            event_id="PSPS-SCE-2025-018", utility="SCE",
            status="planned", affected_customers=12000,
            start_time=datetime(2025, 7, 16, 6, 0),
            estimated_restoration=datetime(2025, 7, 17, 18, 0),
            affected_areas=["Ventura County", "Santa Barbara County"],
        ),
    ]

    AGENCY_ASSIGNMENTS: list[AgencyAssignment] = [
        AgencyAssignment(agency="CAL_FIRE", role="Incident Commander — Paradise Ridge Fire", contact="IC Martinez: (530) 555-0100", resources_committed=35),
        AgencyAssignment(agency="Cal_OES", role="State Emergency Coordination", contact="SOC Watch: (916) 555-0200", resources_committed=10),
        AgencyAssignment(agency="County_FD", role="Structure Protection — LA County", contact="Battalion Chief Lee: (213) 555-0300", resources_committed=20),
        AgencyAssignment(agency="CHP", role="Traffic Control & Evacuation Support", contact="Area Commander: (530) 555-0400", resources_committed=8),
        AgencyAssignment(agency="USFS", role="Federal Land Fire Suppression", contact="Forest Supervisor: (530) 555-0500", resources_committed=12),
        AgencyAssignment(agency="NWS", role="Weather Intelligence & Red Flag Warnings", contact="WFO Sacramento: (916) 555-0600", resources_committed=0),
    ]

    def get_incident(self, incident_id: str) -> Incident | None:
        return self.INCIDENTS.get(incident_id)

    def get_all_incidents(self) -> list[Incident]:
        return list(self.INCIDENTS.values())

    def get_available_resources(self, resource_types: list[str] | None = None) -> list[ResourceAllocation]:
        if resource_types:
            return [r for r in self.RESOURCES if r.resource_type in resource_types]
        return [r for r in self.RESOURCES if r.status == "available"]

    def get_evacuation_info(self) -> EvacuationInfo:
        total_evacuated = sum(z.population for z in self.EVACUATION_ZONES if z.status == "order")
        shelters_open = len(set(s for z in self.EVACUATION_ZONES for s in z.shelters))
        return EvacuationInfo(
            zones=self.EVACUATION_ZONES,
            total_evacuated=total_evacuated,
            shelters_open=shelters_open,
        )

    def get_weather(self, county: str | None = None) -> list[WeatherCondition]:
        if county:
            return [w for w in self.WEATHER if county.lower() in w.location.lower()]
        return self.WEATHER

    def get_psps_events(self) -> list[PSPSEvent]:
        return self.PSPS_EVENTS

    def get_agency_assignments(self) -> list[AgencyAssignment]:
        return self.AGENCY_ASSIGNMENTS

    def create_incident(self, data: dict) -> Incident:
        """Create a new incident from provided data."""
        import uuid
        incident_id = f"CA-NEW-{str(uuid.uuid4())[:6].upper()}"
        incident = Incident(
            incident_id=incident_id,
            name=data.get("name", "New Incident"),
            incident_type=data.get("incident_type", "wildfire"),
            severity=data.get("severity", "moderate"),
            location=data.get("location", "Unknown"),
            county=data.get("county", "Unknown"),
            acres_burned=data.get("acres_burned", 0.0),
            containment_pct=data.get("containment_pct", 0.0),
            lead_agency=data.get("lead_agency", "CAL FIRE"),
            status="active",
            mutual_aid_region=data.get("mutual_aid_region", 1),
        )
        self.INCIDENTS[incident_id] = incident
        return incident
