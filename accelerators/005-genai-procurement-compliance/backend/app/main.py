"""GenAI Procurement Compliance — FastAPI application."""

import os

from fastapi import FastAPI

from app.models.schemas import ChatRequest, ChatResponse
from app.pipeline import process_message
from app.services.mock_service import MockComplianceService

app = FastAPI(
    title="GenAI Procurement Compliance API",
    description="Automated vendor attestation review and compliance scoring for CDT/DGS",
    version="0.1.0",
)

mock_service = MockComplianceService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "genai-procurement-compliance",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return await process_message(request)


@app.get("/api/status")
async def status():
    return {
        "service": "genai-procurement-compliance",
        "version": "0.1.0",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
        "compliance_frameworks": ["EO_N-5-26", "SB_53", "NIST_AI_RMF"],
        "endpoints": ["/health", "/api/chat", "/api/status", "/api/attestations"],
    }


@app.post("/api/attestations")
async def upload_attestation():
    doc = mock_service.create_attestation()
    return {"attestation": doc.model_dump(mode="json")}


@app.get("/api/attestations/{doc_id}/results")
async def get_attestation_results(doc_id: str):
    results = mock_service.get_compliance_results()
    score = mock_service.get_compliance_score()
    return {
        "doc_id": doc_id,
        "score": score.model_dump(),
        "results": [r.model_dump() for r in results],
    }
