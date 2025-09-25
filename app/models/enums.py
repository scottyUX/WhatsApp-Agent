from enum import Enum


class SupportedLanguage(str, Enum):
    """Enum for supported languages with their ISO 639-1 codes."""
    ENGLISH = "en"
    GERMAN = "de"
    SPANISH = "es"


class MediaType(str, Enum):
    """Enum for different types of media that can be attached to messages."""
    IMAGE = "image"
    AUDIO = "audio"
