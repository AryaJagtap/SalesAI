"""
SalesAI V2.0 — FastAPI Application
Main entry point for the backend API server.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models.schemas import HealthResponse
from routers import analysis, transcription

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("=" * 50)
    logger.info("  SalesAI V2.0 — Starting up")
    logger.info("=" * 50)
    logger.info(f"  Gemini API Key: {'✅ Configured' if settings.GEMINI_API_KEY else '❌ Not set'}")
    logger.info(f"  Groq API Key:   {'✅ Configured' if settings.GROQ_API_KEY else '❌ Not set'}")
    logger.info(f"  Gemini Model:   {settings.GEMINI_MODEL}")
    logger.info(f"  Groq Model:     {settings.GROQ_MODEL}")
    logger.info(f"  Whisper Model:  {settings.WHISPER_MODEL}")
    logger.info("=" * 50)
    yield
    logger.info("SalesAI V2.0 — Shutting down")


# Create FastAPI app
app = FastAPI(
    title="SalesAI V2.0",
    description="AI-Powered Sales Call Analysis Co-Pilot",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(analysis.router)
app.include_router(transcription.router)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version="2.0.0",
        gemini_configured=bool(settings.GEMINI_API_KEY),
        groq_configured=bool(settings.GROQ_API_KEY)
    )
