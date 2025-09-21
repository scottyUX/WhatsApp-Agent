"""
Question definitions for the patient intake questionnaire.
Defines all questions with metadata, validation rules, and skip handling.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Question:
    """Individual question definition with metadata."""
    id: str
    text: str
    category: str  # 'basic', 'medical', 'hair_loss'
    required: bool = False
    skip_keywords: List[str] = None
    clarification_prompt: str = ""
    validation_function: Optional[str] = None
    
    def __post_init__(self):
        if self.skip_keywords is None:
            self.skip_keywords = ["skip", "pass", "nein", "next", "prefer not to say"]


# BASIC INFORMATION QUESTIONS (3 questions)
BASIC_QUESTIONS = [
    Question(
        id="basic_country",
        text="What's your country?",
        category="basic_info",
        required=False,
        clarification_prompt="Could you please provide your country? For example: 'United States', 'United Kingdom', or 'Canada'",
        validation_function="validate_location"
    ),
    Question(
        id="basic_age",
        text="What's your age?",
        category="basic_info",
        required=False,
        clarification_prompt="Could you please provide your age? For example: '25' or '45'",
        validation_function="validate_age"
    ),
    Question(
        id="basic_gender",
        text="What's your gender?",
        category="basic_info",
        required=False,
        clarification_prompt="Could you please tell me your gender?",
        validation_function="validate_gender"
    )
]

# MEDICAL BACKGROUND QUESTIONS (3 questions)
MEDICAL_QUESTIONS = [
    Question(
        id="medical_conditions",
        text="Do you have any medical conditions like diabetes, thyroid issues, autoimmune diseases, or anemia?",
        category="medical_info",
        required=False,
        clarification_prompt="Could you please list any medical conditions you have? You can say 'none' if you don't have any",
        validation_function="validate_medical_conditions"
    ),
    Question(
        id="current_medications",
        text="Are you taking any medications or supplements, including blood thinners or treatments for arthritis or depression?",
        category="medical_info",
        required=False,
        clarification_prompt="Could you please list any medications or supplements you're currently taking? You can say 'none' if you don't take any",
        validation_function="validate_medications"
    ),
    Question(
        id="recent_events",
        text="Have you experienced any recent illnesses, surgeries, or significant stress in the last 6 months, including COVID-19, that could trigger temporary hair loss?",
        category="medical_info",
        required=False,
        clarification_prompt="Could you please tell me about any recent health events in the last 6 months? You can say 'none' if nothing recent",
        validation_function="validate_recent_events"
    )
]

# HAIR LOSS BACKGROUND QUESTIONS (3 questions)
HAIR_LOSS_QUESTIONS = [
    Question(
        id="hair_loss_onset",
        text="When did you first notice your hair loss? Was it sudden or gradual?",
        category="hair_loss_info",
        required=False,
        clarification_prompt="Could you please tell me when you first noticed hair loss and whether it happened suddenly or gradually?",
        validation_function="validate_hair_loss_onset"
    ),
    Question(
        id="hair_loss_location",
        text="Where have you noticed hair loss on your scalp (e.g., top, front, or sides)?",
        category="hair_loss_info",
        required=False,
        clarification_prompt="Could you please specify where you've noticed hair loss on your scalp? For example: 'crown', 'hairline', 'sides', or 'all over'",
        validation_function="validate_hair_loss_location"
    ),
    Question(
        id="previous_treatments",
        text="Have you tried any hair loss treatments in the past, and what were the results?",
        category="hair_loss_info",
        required=False,
        clarification_prompt="Could you please tell me about any hair loss treatments you've tried before? You can say 'none' if you haven't tried any",
        validation_function="validate_previous_treatments"
    )
]

# ALL QUESTIONS COMBINED (9 total questions)
ALL_QUESTIONS = BASIC_QUESTIONS + MEDICAL_QUESTIONS + HAIR_LOSS_QUESTIONS

# QUESTION CATEGORIES
QUESTION_CATEGORIES = {
    "basic_info": BASIC_QUESTIONS,
    "medical_info": MEDICAL_QUESTIONS,
    "hair_loss_info": HAIR_LOSS_QUESTIONS
}

def get_question_by_id(question_id: str) -> Optional[Question]:
    """Get a question by its ID."""
    for question in ALL_QUESTIONS:
        if question.id == question_id:
            return question
    return None


def get_questions_by_category(category: str) -> List[Question]:
    """Get all questions for a specific category."""
    return QUESTION_CATEGORIES.get(category, [])


def get_next_question_id(current_question_id: str, category: str) -> Optional[str]:
    """Get the next question ID in a category."""
    questions = get_questions_by_category(category)
    current_index = None
    
    for i, question in enumerate(questions):
        if question.id == current_question_id:
            current_index = i
            break
    
    if current_index is not None and current_index + 1 < len(questions):
        return questions[current_index + 1].id
    
    return None


def is_skip_response(response: str) -> bool:
    """Check if a response indicates the user wants to skip the current question."""
    response_lower = response.lower().strip()
    
    # Check for individual skip keywords
    for question in ALL_QUESTIONS:
        for skip_keyword in question.skip_keywords:
            if skip_keyword in response_lower:
                return True
    
    return False
