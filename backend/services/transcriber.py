"""
SalesAI V2.0 — Audio Transcription Service
Primary: Groq Whisper API (cloud, ultra-fast)
Fallback: Local faster-whisper (offline)
Speaker separation via heuristic scoring + alternating pattern.
"""

import os
import re
import tempfile
import logging
from typing import Optional

from groq import Groq
from pydub import AudioSegment
from faster_whisper import WhisperModel

from config import settings

logger = logging.getLogger(__name__)

# Lazy-load local model only if needed as fallback
_local_model: Optional[WhisperModel] = None


def _get_local_model() -> WhisperModel:
    """Get or initialize the local Whisper model (lazy load, fallback only)."""
    global _local_model
    if _local_model is None:
        logger.info(f"Loading local faster-whisper model: {settings.WHISPER_MODEL}")
        _local_model = WhisperModel(
            settings.WHISPER_MODEL,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE
        )
        logger.info("Local Whisper model loaded successfully")
    return _local_model


# ─── Speaker Detection (Scoring System) ───

# Customer-specific phrases (the person asking questions, stating needs/budget)
CUSTOMER_PHRASES = [
    "i want", "i need", "i'm looking", "i am looking",
    "show me", "my budget", "i prefer", "i like",
    "any discount", "which one", "no,", "no ", "yes,", "yes ",
    "around", "rupees", "dollars", "thousand",
    "i'll take", "i will take", "that's too", "too expensive",
    "something cheaper", "something better", "only",
]

# Sales Agent-specific phrases (the person offering, asking what customer wants)
AGENT_PHRASES = [
    "do you want", "should i show", "let me show", "let me help",
    "we have", "here are", "here is", "these are", "this is the",
    "great choice", "excellent", "perfect",
    "what is your budget", "what's your budget",
    "may i help", "can i help", "how can i help",
    "would you like", "shall i", "allow me",
    "sir", "ma'am", "madam",
    "any specific", "brand preference",
    "we offer", "we also have", "our best",
    "in this range", "within your budget",
    "let me check", "let me get",
]


def _score_speaker(text: str) -> str:
    """
    Score text against customer vs agent phrase lists.
    Returns 'Customer' or 'Sales Agent' based on highest score.
    """
    text_l = text.lower()

    customer_score = sum(1 for phrase in CUSTOMER_PHRASES if phrase in text_l)
    agent_score = sum(1 for phrase in AGENT_PHRASES if phrase in text_l)

    # Questions directed AT the customer are agent speech
    if text_l.endswith("?") or text_l.endswith("? "):
        # Questions containing "you/your" are likely agent asking customer
        if any(w in text_l for w in ["your", "you want", "you like", "you prefer", "you need"]):
            agent_score += 2
        # Questions with "I" are likely customer asking
        elif any(w in text_l for w in ["can i", "do i", "should i"]):
            customer_score += 1

    # Statements with "I" + action are usually customer
    if re.search(r'\bi (want|need|prefer|like|am looking)\b', text_l):
        customer_score += 2

    # Budget amounts are customer responses
    if re.search(r'\d[\d,]*\s*(rupees|dollars|thousand|k\b|lakh)', text_l):
        customer_score += 2

    if customer_score > agent_score:
        return "Customer"
    elif agent_score > customer_score:
        return "Sales Agent"
    else:
        return "Unknown"  # Will use alternating pattern


def _split_merged_segments(text: str) -> list[str]:
    """
    Split a segment that may contain speech from both speakers.
    Splits on question marks followed by a response, or sentence boundaries.
    """
    # Split on "? " followed by a new sentence (likely speaker change)
    parts = re.split(r'(\?\s+)', text)
    if len(parts) <= 1:
        return [text]

    # Re-join question marks with their sentences
    sentences = []
    current = ""
    for part in parts:
        current += part
        if part.strip() == "?":
            continue
        if current.strip():
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())

    return sentences if len(sentences) > 1 else [text]


def _assign_speakers(raw_segments: list[dict]) -> list[dict]:
    """
    Assign speakers to segments using scoring + alternating pattern.
    Also splits merged segments when detected.
    """
    # First pass: split any merged segments and score each
    expanded = []
    for seg in raw_segments:
        text = seg["text"]
        sub_texts = _split_merged_segments(text)

        if len(sub_texts) > 1:
            for sub in sub_texts:
                if sub.strip():
                    expanded.append({
                        "text": sub.strip(),
                        "timestamp": seg.get("timestamp", "00:00"),
                        "start": seg.get("start", 0),
                        "speaker_score": _score_speaker(sub)
                    })
        else:
            expanded.append({
                "text": text,
                "timestamp": seg.get("timestamp", "00:00"),
                "start": seg.get("start", 0),
                "speaker_score": _score_speaker(text)
            })

    if not expanded:
        return []

    # Second pass: resolve "Unknown" using alternating pattern
    # First, find the first segment with a definite speaker
    first_known = "Customer"  # Default: conversations usually start with customer
    for seg in expanded:
        if seg["speaker_score"] != "Unknown":
            first_known = seg["speaker_score"]
            break

    # Now assign all speakers with alternating tiebreaker
    result = []
    prev_speaker = None

    for seg in expanded:
        if seg["speaker_score"] != "Unknown":
            speaker = seg["speaker_score"]
        elif prev_speaker:
            # Alternate from previous speaker
            speaker = "Sales Agent" if prev_speaker == "Customer" else "Customer"
        else:
            speaker = first_known

        prev_speaker = speaker
        result.append({
            "speaker": speaker,
            "text": seg["text"],
            "timestamp": seg["timestamp"]
        })

    return result


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


# ─── Groq Whisper API (Primary — Cloud, Ultra-Fast) ───

# Universal vocabulary prompt to guide Whisper recognition across all industries
WHISPER_PROMPT = (
    "Sales and business conversation between a customer and a sales agent or service provider. "
    # Electronics
    "Samsung, Apple, Nokia, OnePlus, Sony, LG, Xiaomi, Realme, Oppo, Vivo, Dell, HP, Lenovo, "
    "smart TV, microwave, refrigerator, washing machine, laptop, phone, tablet, earbuds, camera, "
    # Real Estate
    "flat, apartment, villa, plot, property, BHK, carpet area, RERA, builder, location, amenities, "
    # Insurance & Finance
    "insurance, LIC, policy, premium, mutual fund, SIP, fixed deposit, term plan, health plan, "
    "stocks, shares, investment, portfolio, IPO, demat, returns, interest rate, EMI, "
    # Automotive
    "car, bike, scooter, mileage, fuel, petrol, diesel, electric, test drive, "
    # Common sales phrases
    "budget, discount, price, cost, brand, model, warranty, offer, exchange, "
    "rupees, thousand, lakh, dollars, "
    "I want to buy, show me, how much, do you have, any discount, "
    "let me show you, we have, great choice, what is your budget."
)


def _transcribe_with_groq(file_path: str) -> Optional[dict]:
    """Transcribe audio using Groq Whisper API with sales-context prompt."""
    if not settings.GROQ_API_KEY:
        return None

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)

        with open(file_path, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                response_format="verbose_json",
                language="en",
                prompt=WHISPER_PROMPT,
            )

        return result
    except Exception as e:
        logger.warning(f"Groq Whisper API failed, falling back to local: {e}")
        return None


def _transcribe_with_local(file_path: str) -> list[dict]:
    """Transcribe using local faster-whisper model (fallback)."""
    model = _get_local_model()
    segments, _ = model.transcribe(
        file_path,
        language="en",
        initial_prompt=WHISPER_PROMPT,
    )
    return [{"start": seg.start, "end": seg.end, "text": seg.text.strip()} for seg in segments]


# ─── Public API ───

def transcribe_audio_file(file_path: str) -> list[dict]:
    """
    Transcribe an audio file with speaker separation.

    Args:
        file_path: Path to the audio file (WAV, MP3, etc.)

    Returns:
        List of segments: [{speaker, text, timestamp}]
    """
    raw_segments = []

    try:
        # Try Groq Whisper first (cloud, 2-5 seconds)
        groq_result = _transcribe_with_groq(file_path)

        if groq_result and hasattr(groq_result, 'segments') and groq_result.segments:
            for seg in groq_result.segments:
                text = seg.get("text", "").strip() if isinstance(seg, dict) else getattr(seg, "text", "").strip()
                start = seg.get("start", 0) if isinstance(seg, dict) else getattr(seg, "start", 0)
                if text:
                    raw_segments.append({
                        "text": text,
                        "timestamp": _format_timestamp(start),
                        "start": start
                    })
            if raw_segments:
                logger.info(f"Groq Whisper: {len(raw_segments)} raw segments transcribed")
                return _assign_speakers(raw_segments)

        # Groq returned text but no segments — use the full text
        if groq_result and hasattr(groq_result, 'text') and groq_result.text:
            full_text = groq_result.text.strip()
            if full_text:
                raw_segments.append({
                    "text": full_text,
                    "timestamp": "00:00",
                    "start": 0
                })
                logger.info("Groq Whisper: transcribed as single segment")
                return _assign_speakers(raw_segments)

        # Fallback to local faster-whisper
        logger.info("Using local faster-whisper fallback")
        local_segments = _transcribe_with_local(file_path)

        for seg in local_segments:
            text = seg["text"]
            if text:
                raw_segments.append({
                    "text": text,
                    "timestamp": _format_timestamp(seg["start"]),
                    "start": seg["start"]
                })

    except Exception as e:
        logger.error(f"Error processing audio file: {e}")
        raise

    return _assign_speakers(raw_segments)


def transcribe_audio_blob(file_path: str) -> str:
    """
    Transcribe a short audio blob (from live mic recording).

    Args:
        file_path: Path to the audio file

    Returns:
        Transcribed text string
    """
    try:
        # Try Groq first
        groq_result = _transcribe_with_groq(file_path)
        if groq_result and hasattr(groq_result, 'text') and groq_result.text:
            return groq_result.text.strip()

        # Fallback to local
        local_segments = _transcribe_with_local(file_path)
        text = " ".join([seg["text"] for seg in local_segments])
        return text.strip()
    except Exception as e:
        logger.error(f"Error transcribing live audio: {e}")
        return ""


