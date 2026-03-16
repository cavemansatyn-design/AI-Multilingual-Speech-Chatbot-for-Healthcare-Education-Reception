"""
Text-to-speech using Edge-TTS.
Output: MP3 bytes or file.
"""

import asyncio
import io
import logging
from pathlib import Path
from typing import Optional, Union

from utils.constants import TTS_VOICES

logger = logging.getLogger(__name__)


def _get_voice(lang_code: str) -> str:
    """Return Edge-TTS voice for language; fallback to English."""
    return TTS_VOICES.get(lang_code, TTS_VOICES["en"])


async def _generate_async(
    text: str,
    voice: str,
) -> bytes:
    """Generate MP3 bytes using edge_tts."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    return buf.getvalue()


def text_to_speech(
    text: str,
    language: str = "en",
    output_path: Optional[Union[str, Path]] = None,
) -> bytes:
    """
    Convert text to speech (MP3).

    Args:
        text: Text to speak.
        language: Language code (en, hi, fr, es, de).
        output_path: If set, also write MP3 to this file.

    Returns:
        MP3 file content as bytes.
    """
    if not text or not text.strip():
        return b""
    voice = _get_voice(language)
    loop = asyncio.new_event_loop()
    try:
        audio_bytes = loop.run_until_complete(_generate_async(text, voice))
    finally:
        loop.close()
    if output_path:
        Path(output_path).write_bytes(audio_bytes)
    return audio_bytes


async def text_to_speech_async(
    text: str,
    language: str = "en",
    output_path: Optional[Union[str, Path]] = None,
) -> bytes:
    """Async version for use in FastAPI."""
    if not text or not text.strip():
        return b""
    voice = _get_voice(language)
    audio_bytes = await _generate_async(text, voice)
    if output_path:
        Path(output_path).write_bytes(audio_bytes)
    return audio_bytes
