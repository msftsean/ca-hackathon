"""GenAI Procurement Compliance — FastAPI application."""

import os
from fastapi import FastAPI

app = FastAPI(
    title="GenAI Procurement Compliance API",
    description="Automated vendor attestation review and compliance scoring for CDT/DGS",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "genai-procurement-compliance",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    }
