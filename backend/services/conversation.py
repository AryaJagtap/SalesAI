"""
SalesAI V2.0 — Conversation Memory Manager
Tracks conversation history per session to prevent repeated AI suggestions.
"""

import time
import logging
from typing import Optional
from threading import Lock

logger = logging.getLogger(__name__)

# In-memory session store (replace with Redis for multi-instance deployments)
_sessions: dict[str, dict] = {}
_lock = Lock()

# Auto-expire sessions after 2 hours
SESSION_TTL_SECONDS = 7200


def _cleanup_expired() -> None:
    """Remove expired sessions."""
    now = time.time()
    expired = [sid for sid, data in _sessions.items() if now - data["last_active"] > SESSION_TTL_SECONDS]
    for sid in expired:
        del _sessions[sid]


def get_history(session_id: str) -> list[dict]:
    """Get conversation history for a session."""
    with _lock:
        _cleanup_expired()
        session = _sessions.get(session_id)
        if session:
            session["last_active"] = time.time()
            return session["history"]
        return []


def add_entry(session_id: str, text: str, analysis: dict) -> None:
    """Add a customer message and its analysis to session history."""
    with _lock:
        if session_id not in _sessions:
            _sessions[session_id] = {
                "history": [],
                "last_active": time.time()
            }

        _sessions[session_id]["history"].append({
            "text": text,
            "sentiment": analysis.get("sentiment", {}).get("label", ""),
            "intent": analysis.get("intent", {}).get("label", ""),
            "suggestion": analysis.get("suggestion", ""),
            "timestamp": time.time()
        })
        _sessions[session_id]["last_active"] = time.time()

        logger.debug(f"Session {session_id}: {len(_sessions[session_id]['history'])} entries")


def clear_session(session_id: str) -> bool:
    """Clear session history."""
    with _lock:
        if session_id in _sessions:
            del _sessions[session_id]
            return True
        return False


def get_session_count() -> int:
    """Return number of active sessions."""
    with _lock:
        _cleanup_expired()
        return len(_sessions)
