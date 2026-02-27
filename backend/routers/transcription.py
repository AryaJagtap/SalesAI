"""
SalesAI V2.0 — Transcription Router
Endpoints for audio file upload and live audio transcription.
"""

import os
import tempfile
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException

from models.schemas import TranscriptionResponse, LiveTranscriptionResponse, TranscriptSegment
from services.transcriber import transcribe_audio_file, transcribe_audio_blob

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["transcription"])

# Max upload size: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_uploaded_file(file: UploadFile = File(...)):
    """
    Transcribe an uploaded audio file with speaker separation.
    Supports WAV, MP3, M4A, OGG, FLAC.
    """
    # Validate file type
    allowed_types = [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"]
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_types)}"
        )

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    tmp_path = tmp.name

    try:
        # Read and validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")

        tmp.write(content)
        tmp.close()

        # Transcribe
        segments = transcribe_audio_file(tmp_path)

        # Build full text
        full_text = " ".join([seg["text"] for seg in segments])

        return TranscriptionResponse(
            segments=[TranscriptSegment(**seg) for seg in segments],
            full_text=full_text
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/transcribe/live", response_model=LiveTranscriptionResponse)
async def transcribe_live_audio(file: UploadFile = File(...)):
    """
    Transcribe a short audio blob from live microphone recording.
    Expects WebM/WAV audio from the browser's MediaRecorder API.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
    tmp_path = tmp.name

    try:
        content = await file.read()
        tmp.write(content)
        tmp.close()

        text = transcribe_audio_blob(tmp_path)

        if not text:
            return LiveTranscriptionResponse(text="", success=False, error="No speech detected")

        return LiveTranscriptionResponse(text=text, success=True)

    except Exception as e:
        logger.error(f"Live transcription failed: {e}")
        return LiveTranscriptionResponse(text="", success=False, error=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
