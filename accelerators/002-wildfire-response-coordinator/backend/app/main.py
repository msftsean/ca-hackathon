"""Wildfire Response Coordinator — FastAPI application."""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.pipeline import WildfirePipeline
from app.models.schemas import ChatRequest, ChatResponse
from app.services.mock_service import MockWildfireService

app = FastAPI(
    title="Wildfire Response Coordinator API",
    description="AI-powered emergency coordination for CAL FIRE and Cal OES",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = WildfirePipeline()
mock_service = MockWildfireService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "wildfire-response-coordinator",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message through the 3-agent pipeline."""
    return await pipeline.process(request)


@app.get("/api/status")
async def status():
    """Return service status and configuration."""
    return {
        "service": "wildfire-response-coordinator",
        "version": "0.1.0",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
        "agents": ["query_agent", "router_agent", "action_agent"],
        "capabilities": ["incident_command", "resource_management", "evacuation_ops", "weather_ops", "utility_coordination", "interagency"],
    }


@app.get("/api/incidents")
async def list_incidents():
    """List all incidents."""
    incidents = mock_service.get_all_incidents()
    return [
        {
            "incident_id": i.incident_id,
            "name": i.name,
            "incident_type": i.incident_type,
            "severity": i.severity,
            "location": i.location,
            "county": i.county,
            "acres_burned": i.acres_burned,
            "containment_pct": i.containment_pct,
            "status": i.status,
            "lead_agency": i.lead_agency,
        }
        for i in incidents
    ]


class CreateIncidentRequest(BaseModel):
    name: str
    incident_type: str = "wildfire"
    severity: str = "moderate"
    location: str = ""
    county: str = ""
    acres_burned: float = 0.0
    lead_agency: str = "CAL FIRE"
    mutual_aid_region: int = 1


@app.post("/api/incidents")
async def create_incident(request: CreateIncidentRequest):
    """Create a new incident."""
    incident = mock_service.create_incident(request.model_dump())
    return incident


@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get incident details by ID."""
    incident = mock_service.get_incident(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@app.get("/api/resources/available")
async def get_available_resources():
    """Get available resources."""
    resources = mock_service.get_available_resources()
    return resources


@app.get("/api/weather")
async def get_weather(county: str | None = None):
    """Get fire weather conditions."""
    weather = mock_service.get_weather(county)
    return weather
