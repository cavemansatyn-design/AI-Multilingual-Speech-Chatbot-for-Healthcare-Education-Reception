#!/usr/bin/env python3
"""
CLI demo: interactive symptom chatbot with language selection, follow-up, report, and TTS.
Run from project root: python demo/cli_chatbot.py
"""

import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.constants import SUPPORTED_LANGUAGES
from services.nlp_service import (
    extract_symptoms_from_text,
    get_next_follow_up,
    apply_follow_up_answer,
    build_extraction_result_from_state,
)
from models.symptom_model import SymptomFollowUpState
from services.report_service import generate_report
from services.translation_service import translate_to_english, translate_from_english
from services.tts_service import text_to_speech


def select_language() -> str:
    print("\nSelect language / Choisir la langue / भाषा चुनें:")
    for code, name in SUPPORTED_LANGUAGES.items():
        print(f"  {code}: {name}")
    while True:
        code = input("Enter code (default en): ").strip().lower() or "en"
        if code in SUPPORTED_LANGUAGES:
            return code
        print("Invalid. Use: en, hi, fr, es, de")


def play_audio(audio_bytes: bytes) -> None:
    """Play MP3 bytes using system default or a simple fallback."""
    if not audio_bytes:
        return
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            f.flush()
            path = f.name
        try:
            import platform
            if platform.system() == "Windows":
                import os
                os.system(f'start /wait "" "{path}"')
            elif platform.system() == "Darwin":
                import subprocess
                subprocess.run(["afplay", path], check=False)
            else:
                import subprocess
                subprocess.run(["xdg-open", path], check=False)
        finally:
            Path(path).unlink(missing_ok=True)
    except Exception as e:
        print(f"(Could not play audio: {e})")


def main() -> None:
    print("=== Multilingual Speech-Based Chatbot (CLI Demo) ===\n")
    language = select_language()
    name = input("Enter your name: ").strip() or "User"
    print(f"\nHello, {name}. Describe your symptoms (e.g. headache, fever, cough). Type 'quit' to exit.\n")

    state: SymptomFollowUpState | None = None

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        # Translate to English for NLP
        text_en = translate_to_english(user_input, language) if language != "en" else user_input

        if state is not None and state.symptoms:
            # Follow-up
            state = apply_follow_up_answer(state, text_en)
            state, next_q = get_next_follow_up(state)
            if next_q:
                reply_en = next_q
            else:
                result = build_extraction_result_from_state(state)
                report = generate_report(
                    symptoms=result.symptoms,
                    frequency=result.frequency,
                    severity=result.severity,
                    duration=result.duration,
                    notes=result.notes,
                )
                reply_en = report.report_text
                print("\n--- Generated Report ---")
                print(reply_en)
                print("------------------------\n")
                state = None
        else:
            result = extract_symptoms_from_text(text_en)
            if not result.symptoms:
                reply_en = "I didn't identify any known symptoms. Could you describe how you're feeling? (e.g. headache, fever, cough)"
                state = None
            else:
                state = SymptomFollowUpState(symptoms=result.symptoms)
                state, next_q = get_next_follow_up(state)
                reply_en = next_q or "Thank you."

        reply = translate_from_english(reply_en, language) if language != "en" else reply_en
        print(f"Bot: {reply}\n")

        # TTS
        try:
            audio_bytes = text_to_speech(reply, language=language)
            if audio_bytes:
                play_audio(audio_bytes)
        except Exception as e:
            print(f"(TTS skipped: {e})\n")


if __name__ == "__main__":
    main()
