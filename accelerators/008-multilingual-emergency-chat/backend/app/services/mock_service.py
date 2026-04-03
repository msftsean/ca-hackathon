"""Comprehensive mock data for Multilingual Emergency Chatbot."""

from datetime import datetime, timedelta

from app.models.schemas import (
    AirQualityReport,
    EmergencyAlert,
    EvacuationOrder,
    ShelterInfo,
)


class MockEmergencyService:
    """Provides mock emergency data for development and testing."""

    def __init__(self) -> None:
        self._now = datetime.now()

    # ---- alerts ---------------------------------------------------------

    def get_alerts(self, emergency_type: str | None = None) -> list[EmergencyAlert]:
        alerts = self._all_alerts()
        if emergency_type:
            alerts = [a for a in alerts if a.emergency_type == emergency_type]
        return alerts

    def _all_alerts(self) -> list[EmergencyAlert]:
        n = self._now
        return [
            EmergencyAlert(
                alert_id="ALERT-2025-001",
                title="Wildfire Evacuation Warning — Butte County",
                description="A wildfire evacuation WARNING is in effect for communities in eastern Butte County.",
                severity="severe",
                emergency_type="wildfire",
                affected_areas=["Paradise", "Magalia", "Stirling City"],
                issued_at=n - timedelta(hours=2),
                expires_at=n + timedelta(hours=22),
                instructions="Prepare to evacuate. Gather essential items. Monitor local news.",
                source="Cal OES / CAL FIRE",
            ),
            EmergencyAlert(
                alert_id="ALERT-2025-002",
                title="Flood Watch — Sacramento River",
                description="Flood watch in effect for low-lying areas along the Sacramento River.",
                severity="moderate",
                emergency_type="flood",
                affected_areas=["Sacramento", "West Sacramento", "Yolo County"],
                issued_at=n - timedelta(hours=6),
                expires_at=n + timedelta(hours=18),
                instructions="Avoid flood-prone areas. Do not drive through standing water.",
                source="Cal OES / NWS",
            ),
            EmergencyAlert(
                alert_id="ALERT-2025-003",
                title="Earthquake Advisory — Bay Area",
                description="A 4.2 magnitude earthquake was detected near Hayward. Aftershocks possible.",
                severity="minor",
                emergency_type="earthquake",
                affected_areas=["Hayward", "Fremont", "Oakland", "San Francisco"],
                issued_at=n - timedelta(hours=1),
                expires_at=n + timedelta(hours=12),
                instructions="Drop, cover, hold on. Check for structural damage. Report gas leaks.",
                source="Cal OES / USGS",
            ),
            EmergencyAlert(
                alert_id="ALERT-2025-004",
                title="Spare the Air — Central Valley",
                description="Air quality alert due to wildfire smoke drifting into the Central Valley.",
                severity="moderate",
                emergency_type="wildfire",
                affected_areas=["Fresno", "Bakersfield", "Modesto", "Stockton"],
                issued_at=n - timedelta(hours=4),
                expires_at=n + timedelta(hours=20),
                instructions="Limit outdoor activity. Use N95 masks. Keep windows closed.",
                source="CARB / SJVAPCD",
            ),
            EmergencyAlert(
                alert_id="ALERT-2025-005",
                title="Hazmat Spill — I-5 Corridor",
                description="A chemical spill has been reported on Interstate 5 near Kettleman City.",
                severity="extreme",
                emergency_type="hazmat",
                affected_areas=["Kettleman City", "Avenal", "Coalinga"],
                issued_at=n - timedelta(minutes=45),
                expires_at=n + timedelta(hours=8),
                instructions="Shelter in place. Close all windows and doors. Avoid the area.",
                source="Cal OES / CHP",
            ),
            EmergencyAlert(
                alert_id="ALERT-2025-006",
                title="Tsunami Watch — Northern Coast",
                description="Tsunami watch issued following a 7.1 earthquake in the Pacific.",
                severity="severe",
                emergency_type="tsunami",
                affected_areas=["Crescent City", "Eureka", "Fort Bragg"],
                issued_at=n - timedelta(minutes=30),
                expires_at=n + timedelta(hours=6),
                instructions="Move to higher ground immediately if near the coast.",
                source="Cal OES / NWS / PTWC",
            ),
        ]

    # ---- evacuation orders ----------------------------------------------

    def get_evacuation_orders(
        self, emergency_type: str | None = None
    ) -> list[EvacuationOrder]:
        n = self._now
        orders = [
            EvacuationOrder(
                order_id="EVAC-2025-001",
                zone_name="Butte County Zone A",
                status="mandatory",
                issued_at=n - timedelta(hours=3),
                instructions="Leave immediately via Skyway Rd south to Chico.",
                routes=["Skyway Rd south", "Clark Rd south", "Pentz Rd south"],
            ),
            EvacuationOrder(
                order_id="EVAC-2025-002",
                zone_name="Butte County Zone B",
                status="warning",
                issued_at=n - timedelta(hours=1),
                instructions="Prepare to leave. Pack essentials and be ready.",
                routes=["Neal Rd south", "Honey Run Rd west"],
            ),
            EvacuationOrder(
                order_id="EVAC-2025-003",
                zone_name="Kettleman City Area",
                status="advisory",
                issued_at=n - timedelta(minutes=30),
                instructions="Shelter in place. Monitor for updates.",
                routes=["SR-41 north", "I-5 south (when cleared)"],
            ),
        ]
        return orders

    # ---- shelters -------------------------------------------------------

    def get_shelters(self, location: str | None = None) -> list[ShelterInfo]:
        return [
            ShelterInfo(
                shelter_id="SH-001",
                name="Chico Community Center",
                address="545 Vallombrosa Ave",
                city="Chico",
                county="Butte",
                capacity=350,
                current_occupancy=127,
                accepts_pets=True,
                ada_accessible=True,
                status="open",
                distance_miles=12.3,
            ),
            ShelterInfo(
                shelter_id="SH-002",
                name="Silver Dollar Fairgrounds",
                address="2357 Fair St",
                city="Chico",
                county="Butte",
                capacity=800,
                current_occupancy=412,
                accepts_pets=True,
                ada_accessible=True,
                status="open",
                distance_miles=14.1,
            ),
            ShelterInfo(
                shelter_id="SH-003",
                name="Sacramento Convention Center",
                address="1400 J St",
                city="Sacramento",
                county="Sacramento",
                capacity=1200,
                current_occupancy=89,
                accepts_pets=False,
                ada_accessible=True,
                status="open",
                distance_miles=85.0,
            ),
            ShelterInfo(
                shelter_id="SH-004",
                name="Oroville Armory",
                address="2640 S 5th Ave",
                city="Oroville",
                county="Butte",
                capacity=200,
                current_occupancy=198,
                accepts_pets=False,
                ada_accessible=True,
                status="full",
                distance_miles=22.5,
            ),
            ShelterInfo(
                shelter_id="SH-005",
                name="Red Bluff Community Center",
                address="1500 S Jackson St",
                city="Red Bluff",
                county="Tehama",
                capacity=250,
                current_occupancy=0,
                accepts_pets=True,
                ada_accessible=False,
                status="open",
                distance_miles=45.0,
            ),
            ShelterInfo(
                shelter_id="SH-006",
                name="Yuba City Shelter",
                address="1201 Civic Center Blvd",
                city="Yuba City",
                county="Sutter",
                capacity=300,
                current_occupancy=150,
                accepts_pets=True,
                ada_accessible=True,
                status="open",
                distance_miles=55.0,
            ),
        ]

    # ---- air quality ----------------------------------------------------

    def get_air_quality(self, location: str | None = None) -> AirQualityReport:
        reports: dict[str, AirQualityReport] = {
            "sacramento": AirQualityReport(
                location="Sacramento",
                aqi=142,
                category="unhealthy_sensitive",
                pollutant="PM2.5",
                health_guidance="People with respiratory conditions should limit outdoor activity.",
                forecast=[
                    {"day": "Tomorrow", "aqi": 120, "category": "unhealthy_sensitive"},
                    {"day": "Day After", "aqi": 95, "category": "moderate"},
                ],
            ),
            "fresno": AirQualityReport(
                location="Fresno",
                aqi=178,
                category="unhealthy",
                pollutant="PM2.5",
                health_guidance="Everyone should reduce prolonged outdoor exertion.",
                forecast=[
                    {"day": "Tomorrow", "aqi": 165, "category": "unhealthy"},
                    {"day": "Day After", "aqi": 140, "category": "unhealthy_sensitive"},
                ],
            ),
            "default": AirQualityReport(
                location="California (General)",
                aqi=85,
                category="moderate",
                pollutant="PM2.5",
                health_guidance="Air quality is acceptable. Unusually sensitive people should limit prolonged outdoor exertion.",
                forecast=[
                    {"day": "Tomorrow", "aqi": 75, "category": "moderate"},
                    {"day": "Day After", "aqi": 60, "category": "moderate"},
                ],
            ),
        }
        if location:
            key = location.lower()
            for k, v in reports.items():
                if k in key or key in k:
                    return v
        return reports["default"]
