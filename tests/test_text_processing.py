"""Tests for text processing utilities."""

import pytest
from utils.text_processing import normalize_text, tokenize


def test_normalize_empty():
    assert normalize_text("") == ""


def test_normalize_lowercase():
    assert normalize_text("HELLO") == "hello"


def test_normalize_punctuation():
    assert normalize_text("hello, world!") == "hello world"


def test_tokenize():
    assert tokenize("a b c") == ["a", "b", "c"]
    assert tokenize(normalize_text("  one   two  ")) == ["one", "two"]
