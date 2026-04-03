"""EDD Claims Assistant — FastAPI application."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EDD Claims Assistant API",
    description="AI-powered claims status and eligibility assistant for EDD",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "edd-claims-assistant",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    }
