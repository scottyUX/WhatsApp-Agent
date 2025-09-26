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


class SchedulingStep(str, Enum):
    """Enumeration of conversation steps in the scheduling process."""
    INITIAL_CONTACT = "initial_contact"
    BASIC_INFO = "basic_info"
    CONSULTATION_SCHEDULING = "consultation_scheduling"
    ADDITIONAL_INFO = "additional_info"
    CLOSURE = "closure"


class Gender(str, Enum):
    """Gender options for patient profiles."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
