"""
Multilingual translation using deep-translator.
Supported: English, Hindi, French, Spanish, German.
"""

import logging
from typing import Optional

from deep_translator import GoogleTranslator
from utils.constants import SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

# deep-translator language codes (Google)
_LANG_CODES = {
    "en": "en",
    "hi": "hi",
    "fr": "fr",
    "es": "es",
    "de": "de",
}


def translate_text(
    text: str,
    source_lang: str = "auto",
    target_lang: str = "en",
) -> str:
    """
    Translate text to target language.

    Args:
        text: Input text.
        source_lang: Source language code or "auto" for detection.
        target_lang: Target language code (en, hi, fr, es, de).

    Returns:
        Translated string. Returns original if translation fails.
    """
    if not text or not text.strip():
        return text
    target = _LANG_CODES.get(target_lang, "en")
    try:
        if source_lang == "auto":
            translator = GoogleTranslator(source="auto", target=target)
        else:
            src = _LANG_CODES.get(source_lang, "en")
            translator = GoogleTranslator(source=src, target=target)
        return translator.translate(text)
    except Exception as e:
        logger.warning("Translation failed: %s", e)
        return text


def translate_to_english(text: str, source_lang: str = "auto") -> str:
    """Convenience: translate input to English for NLP pipeline."""
    return translate_text(text, source_lang=source_lang, target_lang="en")


def translate_from_english(text: str, target_lang: str) -> str:
    """Convenience: translate English response to user language."""
    if target_lang == "en":
        return text
    return translate_text(text, source_lang="en", target_lang=target_lang)
