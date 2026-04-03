"""Permit Streamliner — FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.schemas import ChatRequest, ChatResponse, ZoningResult
from app.pipeline import PermitPipeline
from app.services.mock_service import MockPermitService

settings = get_settings()

app = FastAPI(
    title="Permit Streamliner API",
    description="AI-powered permit intake and routing for OPR, HCD, and DCA",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = PermitPipeline()
mock_service = MockPermitService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "permit-streamliner",
        "mock_mode": settings.use_mock_services,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await pipeline.process(request)


@app.get("/api/status")
async def status():
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "mock_mode": settings.use_mock_services,
        "supported_permit_types": settings.supported_permit_types.split(","),
        "max_review_days": settings.max_review_days,
    }


@app.get("/api/applications")
async def list_applications():
    return mock_service.get_sample_applications()


@app.get("/api/zoning/check")
async def zoning_check(address: str = "123 Main St") -> dict:
    return mock_service.get_zoning_info(address)
