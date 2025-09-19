#!/usr/bin/env python3
"""
Debug the questionnaire flow issue.
"""

import asyncio
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.agents.specialized_agents.questionnaire_manager import create_questionnaire_manager
from app.agents.specialized_agents.scheduling_models import ConversationState, PatientProfile, SchedulingStep

async def debug_questionnaire_flow():
    """Debug the questionnaire flow step by step."""
    print("🐛 Debugging Questionnaire Flow")
    print("=" * 50)
    
    # Initialize questionnaire manager
    questionnaire_manager = create_questionnaire_manager()
    conversation_state = ConversationState(
        user_id="test_user",
        phone_number="+18312959447",
        current_step=SchedulingStep.QUESTIONNAIRE,
        patient_profile=PatientProfile()
    )
    
    # Start questionnaire
    print("1. Starting questionnaire...")
    response1 = questionnaire_manager.start_questionnaire(conversation_state)
    print(f"Response: {response1}")
    print(f"Current question ID: {conversation_state.current_question_id}")
    print(f"Questionnaire step: {conversation_state.patient_profile.questionnaire_step}")
    print()
    
    # Answer first question (country)
    print("2. Answering country question...")
    success, response2, next_action = questionnaire_manager.process_response(
        conversation_state.current_question_id,
        "usa",
        conversation_state,
        save_to_db=False
    )
    print(f"Success: {success}")
    print(f"Response: {response2}")
    print(f"Next action: {next_action}")
    print(f"Current question ID: {conversation_state.current_question_id}")
    print(f"Questionnaire step: {conversation_state.patient_profile.questionnaire_step}")
    print(f"Responses count: {len(conversation_state.patient_profile.questionnaire_responses)}")
    print()
    
    # Get next question
    print("3. Getting next question...")
    next_question = questionnaire_manager.get_next_question(conversation_state)
    if next_question:
        print(f"Next question: {next_question['text']}")
        print(f"Question ID: {next_question['id']}")
        print(f"Current question ID: {conversation_state.current_question_id}")
    else:
        print("No next question found!")
    print()
    
    # Answer second question (age)
    print("4. Answering age question...")
    success, response3, next_action = questionnaire_manager.process_response(
        conversation_state.current_question_id,
        "52",
        conversation_state,
        save_to_db=False
    )
    print(f"Success: {success}")
    print(f"Response: {response3}")
    print(f"Next action: {next_action}")
    print(f"Current question ID: {conversation_state.current_question_id}")
    print(f"Questionnaire step: {conversation_state.patient_profile.questionnaire_step}")
    print(f"Responses count: {len(conversation_state.patient_profile.questionnaire_responses)}")
    print()
    
    # Get next question after age
    print("5. Getting next question after age...")
    next_question = questionnaire_manager.get_next_question(conversation_state)
    if next_question:
        print(f"Next question: {next_question['text']}")
        print(f"Question ID: {next_question['id']}")
        print(f"Current question ID: {conversation_state.current_question_id}")
    else:
        print("No next question found!")
        print(f"Questionnaire step: {conversation_state.patient_profile.questionnaire_step}")
        print(f"Current category index: {questionnaire_manager.current_category_index}")
    print()
    
    print("✅ Debug completed!")

if __name__ == "__main__":
    asyncio.run(debug_questionnaire_flow())
