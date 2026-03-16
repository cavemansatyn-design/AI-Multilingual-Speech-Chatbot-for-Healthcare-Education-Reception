"""
Application-wide constants for the multilingual speech chatbot.
"""

# Supported languages and their codes for translation and TTS
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
}

# Edge-TTS voice mapping (language code -> voice name)
TTS_VOICES = {
    "en": "en-US-JennyNeural",
    "hi": "hi-IN-SwaraNeural",
    "fr": "fr-FR-DeniseNeural",
    "es": "es-ES-ElviraNeural",
    "de": "de-DE-KatjaNeural",
}

# Frequency options for symptom follow-up
FREQUENCY_OPTIONS = [
    "rarely",
    "occasionally",
    "frequently",
    "all the time",
    "daily",
    "weekly",
]

# Severity scale
SEVERITY_MIN = 1
SEVERITY_MAX = 10

# User roles for RBAC
ROLES = ["user", "admin", "doctor"]

# Default symptom list path (relative to project root)
DEFAULT_SYMPTOM_LIST_PATH = "data/symptom_list.json"
