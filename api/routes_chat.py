"""
Chat endpoints: text and audio input → NLP → report → translation → TTS.
"""

import base64
import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException

from app.config import Settings
from app.dependencies import get_config, get_current_user_optional
from database.mongodb_client import MongoDBClient
from models.symptom_model import SymptomFollowUpState
from models.user_model import UserInDB
from services.nlp_service import (
    extract_symptoms_from_text,
    get_next_follow_up,
    apply_follow_up_answer,
    build_extraction_result_from_state,
)
from services.translation_service import translate_to_english, translate_from_english
from services.report_service import generate_report
from services.asr_service import transcribe_audio
from services.tts_service import text_to_speech_async

router = APIRouter()


@router.post("/text")
async def chat_text(
    text: str = Form(...),
    language: str = Form("en"),
    state_json: Optional[str] = Form(None),
    config: Settings = Depends(get_config),
    current_user: Optional[UserInDB] = Depends(get_current_user_optional),
):
    """
    Process text input: translate to EN → NLP (symptom extraction / follow-up) → report → translate back → optional TTS.
    If state_json is provided, treat as follow-up answer and update state.
    Returns bot reply, updated state, and optional base64 MP3.
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    # Translate input to English for NLP
    text_en = translate_to_english(text, source_lang=language) if language != "en" else text

    # Load previous state if any
    state = None
    if state_json:
        try:
            data = json.loads(state_json)
            state = SymptomFollowUpState(**data)
        except (json.JSONDecodeError, TypeError):
            pass

    reply_en: str
    new_state: Optional[SymptomFollowUpState] = None
    report_text: Optional[str] = None
    structured: Optional[dict] = None

    if state is not None and state.symptoms:
        # Follow-up mode: apply answer and get next question or final report
        state = apply_follow_up_answer(state, text_en)
        state, next_q = get_next_follow_up(state)
        if next_q:
            reply_en = next_q
            new_state = state
        else:
            # All follow-ups done → generate report
            result = build_extraction_result_from_state(state)
            report = generate_report(
                symptoms=result.symptoms,
                frequency=result.frequency,
                severity=result.severity,
                duration=result.duration,
                notes=result.notes,
            )
            report_text = report.report_text
            structured = report.structured_data.model_dump() if report.structured_data else None
            reply_en = report_text
            new_state = None  # Reset for next session
    else:
        # New session: extract symptoms
        result = extract_symptoms_from_text(text_en)
        if not result.symptoms:
            reply_en = "I didn't identify any known symptoms. Could you describe how you're feeling in more detail? (e.g. headache, fever, cough)"
            new_state = None
        else:
            state = SymptomFollowUpState(symptoms=result.symptoms)
            state, next_q = get_next_follow_up(state)
            reply_en = next_q or "Thank you."
            new_state = state

    # Translate reply to user language
    reply = translate_from_english(reply_en, language) if language != "en" else reply_en

    # Optional: generate TTS (base64 MP3)
    audio_b64: Optional[str] = None
    try:
        audio_bytes = await text_to_speech_async(reply, language=language)
        if audio_bytes:
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    except Exception:
        pass

    return {
        "reply": reply,
        "reply_en": reply_en,
        "report_text": report_text,
        "structured": structured,
        "state": new_state.model_dump() if new_state else None,
        "audio_base64": audio_b64,
    }


@router.post("/audio")
async def chat_audio(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    state_json: Optional[str] = Form(None),
    config: Settings = Depends(get_config),
    current_user: Optional[UserInDB] = Depends(get_current_user_optional),
):
    """
    Process audio upload: transcribe (Whisper) → then same pipeline as /chat/text.
    """
    contents = await audio.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Audio file is required")
    try:
        text_en, detected_lang = transcribe_audio(audio_bytes=contents, translate_to_en=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Transcription failed: {str(e)}")
    if not text_en.strip():
        raise HTTPException(status_code=400, detail="No speech detected in audio")
    # Inline same pipeline as /chat/text using transcribed text (already in English)
    state = None
    if state_json:
        try:
            state = SymptomFollowUpState(**json.loads(state_json))
        except Exception:
            pass

    reply_en: str
    new_state: Optional[SymptomFollowUpState] = None
    report_text: Optional[str] = None
    structured: Optional[dict] = None

    if state is not None and state.symptoms:
        state = apply_follow_up_answer(state, text_en)
        state, next_q = get_next_follow_up(state)
        if next_q:
            reply_en = next_q
            new_state = state
        else:
            result = build_extraction_result_from_state(state)
            report = generate_report(
                symptoms=result.symptoms,
                frequency=result.frequency,
                severity=result.severity,
                duration=result.duration,
                notes=result.notes,
            )
            report_text = report.report_text
            structured = report.structured_data.model_dump() if report.structured_data else None
            reply_en = report_text
            new_state = None
    else:
        result = extract_symptoms_from_text(text_en)
        if not result.symptoms:
            reply_en = "I didn't identify any known symptoms. Could you describe how you're feeling in more detail?"
            new_state = None
        else:
            state = SymptomFollowUpState(symptoms=result.symptoms)
            state, next_q = get_next_follow_up(state)
            reply_en = next_q or "Thank you."
            new_state = state

    reply = translate_from_english(reply_en, language) if language != "en" else reply_en
    audio_b64: Optional[str] = None
    try:
        audio_bytes = await text_to_speech_async(reply, language=language)
        if audio_bytes:
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    except Exception:
        pass

    return {
        "transcribed": text_en,
        "reply": reply,
        "reply_en": reply_en,
        "report_text": report_text,
        "structured": structured,
        "state": new_state.model_dump() if new_state else None,
        "audio_base64": audio_b64,
    }
