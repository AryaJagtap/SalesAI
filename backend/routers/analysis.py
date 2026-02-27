"""
SalesAI V2.0 — Analysis Router
Endpoints for AI-powered sales conversation analysis.
"""

import uuid
from fastapi import APIRouter, HTTPException

from models.schemas import AnalyzeRequest, AnalysisResponse, SessionClearResponse
from services import ai_engine, conversation

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze customer text for sentiment, intent, entities, and get a sales suggestion.
    Uses conversation history to prevent repeated suggestions.
    """
    try:
        # Get conversation history for this session
        history = conversation.get_history(request.session_id)

        # Run analysis with context
        result = ai_engine.analyze(request.text, history, speed_first=request.speed_first, preferred_engine=request.preferred_engine)

        # Store in conversation memory
        conversation.add_entry(request.session_id, request.text, result)

        return AnalysisResponse(
            sentiment=result.get("sentiment", {"label": "Neutral", "score": 0.5}),
            intent=result.get("intent", {"label": "Unknown", "score": 0.0}),
            entities=result.get("entities", []),
            suggestion=result.get("suggestion", ""),
            reasoning=result.get("reasoning", ""),
            engine_used=result.get("engine_used", "unknown")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/session/new")
async def create_session():
    """Create a new conversation session and return its ID."""
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}


@router.delete("/session/{session_id}", response_model=SessionClearResponse)
async def clear_session(session_id: str):
    """Clear conversation history for a session."""
    conversation.clear_session(session_id)
    return SessionClearResponse(success=True, message=f"Session {session_id} cleared")
