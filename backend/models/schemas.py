"""
SalesAI V2.0 — Pydantic Schemas
Request and response models for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ─── Analysis ───

class SentimentResult(BaseModel):
    label: str = Field(description="Positive, Neutral, or Negative")
    score: float = Field(ge=0.0, le=1.0, description="Confidence score")


class IntentResult(BaseModel):
    label: str = Field(description="Detected intent")
    score: float = Field(ge=0.0, le=1.0, description="Confidence score")


class EntityResult(BaseModel):
    entity: str = Field(description="Entity type (Brand, Product, Budget, etc.)")
    value: str = Field(description="Extracted value")


class AnalysisResponse(BaseModel):
    sentiment: SentimentResult
    intent: IntentResult
    entities: list[EntityResult] = []
    suggestion: str = ""
    reasoning: str = ""
    engine_used: str = "gemini"


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, description="Customer text to analyze")
    session_id: str = Field(default="default", description="Session ID for conversation memory")
    speed_first: bool = Field(default=False, description="If True, prioritize speed (Groq first) for live mode")
    preferred_engine: str = Field(default="auto", description="Preferred engine: 'gemini', 'groq', or 'auto'")


# ─── Transcription ───

class TranscriptSegment(BaseModel):
    speaker: str = Field(description="Speaker label: Customer or Sales Agent")
    text: str
    timestamp: str = Field(default="", description="Timestamp in MM:SS format")


class TranscriptionResponse(BaseModel):
    segments: list[TranscriptSegment] = []
    full_text: str = ""


class LiveTranscriptionResponse(BaseModel):
    text: str = ""
    success: bool = True
    error: Optional[str] = None


# ─── Session ───

class SessionClearResponse(BaseModel):
    success: bool = True
    message: str = "Session cleared"


# ─── Health ───

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "2.0.0"
    gemini_configured: bool = False
    groq_configured: bool = False
