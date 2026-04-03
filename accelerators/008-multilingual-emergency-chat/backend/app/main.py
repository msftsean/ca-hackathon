"""Multilingual Emergency Chatbot — FastAPI application."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import ChatRequest, ChatResponse
from app.pipeline import process_message

app = FastAPI(
    title="Multilingual Emergency Chatbot API",
    description="Multilingual emergency information assistant for Cal OES",
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
        "service": "multilingual-emergency-chat",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return await process_message(request)


@app.get("/api/status")
async def status():
    return {
        "service": "multilingual-emergency-chat",
        "version": "0.1.0",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
        "supported_languages": "en,es,zh,vi,tl,ko,hy,fa,ar,ja,ru,th,km,hmn,lo".split(","),
        "endpoints": ["/health", "/api/chat", "/api/status"],
    }
