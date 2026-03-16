"""
Speech-to-text using OpenAI Whisper.
Process: audio -> transcribe -> detect language -> return text (and optional English).
"""

import io
import logging
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Union

logger = logging.getLogger(__name__)

# Lazy load whisper to avoid slow startup when not using ASR
_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            _whisper_model = whisper.load_model("base")
        except Exception as e:
            logger.warning("Whisper model load failed: %s", e)
            raise
    return _whisper_model


def transcribe_audio(
    audio_path: Optional[Union[str, Path]] = None,
    audio_bytes: Optional[bytes] = None,
    language: Optional[str] = None,
    translate_to_en: bool = True,
) -> Tuple[str, str]:
    """
    Transcribe audio to text using Whisper.

    Args:
        audio_path: Path to audio file (wav, mp3, etc.).
        audio_bytes: In-memory audio data (used if audio_path not set).
        language: Hint language code (e.g. "en"). None for auto-detect.
        translate_to_en: If True, return also English translation when detected lang != en.

    Returns:
        (transcribed_text, detected_or_hint_language).
        If translate_to_en and detected != en, transcribed_text can be English translation.
    """
    if audio_path is None and audio_bytes is None:
        raise ValueError("Provide either audio_path or audio_bytes")
    model = _get_whisper_model()
    if audio_path is not None:
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(str(path))
        result = model.transcribe(
            str(path),
            language=language or None,
            task="translate" if translate_to_en else "transcribe",
        )
    else:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            try:
                result = model.transcribe(
                    tmp.name,
                    language=language or None,
                    task="translate" if translate_to_en else "transcribe",
                )
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    text = (result.get("text") or "").strip()
    detected = result.get("language", "en")
    return text, detected
