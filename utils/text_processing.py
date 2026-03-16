"""
Text normalization and tokenization utilities for NLP pipeline.
"""

import re
from typing import List


def normalize_text(text: str) -> str:
    """
    Normalize input text: lowercase, remove punctuation, trim whitespace.

    Args:
        text: Raw input string.

    Returns:
        Normalized string.
    """
    if not text or not isinstance(text, str):
        return ""
    # Lowercase
    text = text.lower().strip()
    # Remove punctuation (keep alphanumeric and spaces)
    text = re.sub(r"[^\w\s]", "", text)
    # Collapse multiple spaces and trim
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    """
    Tokenize normalized text into a list of words.

    Args:
        text: Normalized string (prefer normalize_text first).

    Returns:
        List of tokens (words).
    """
    if not text:
        return []
    return text.split()
