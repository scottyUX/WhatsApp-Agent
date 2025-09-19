#!/usr/bin/env python3
"""
Test script for questionnaire integration with scheduling agent.
This tests the questionnaire flow without database integration.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.specialized_agents.scheduling_agent import create_scheduling_service
from app.agents.specialized_agents.scheduling_models import PatientProfile, SchedulingStep


async def test_questionnaire_flow():
    """Test the complete questionnaire flow."""
    print("🧪 Testing Questionnaire Integration with Scheduling Agent")
    print("=" * 60)
    
    # Create scheduling service
    scheduling_service = create_scheduling_service()
    
    # Create a patient profile with basic info already collected
    patient_profile = PatientProfile(
        name="John Doe",
        phone="+1234567890",
        email="john@example.com"
    )
    
    # Simulate the flow
    current_step = SchedulingStep.CONSULTATION_SCHEDULING
    current_profile = patient_profile
    
    print(f"📋 Starting with step: {current_step.value}")
    print(f"👤 Patient: {current_profile.name}")
    print()
    
    # Step 1: Schedule appointment (simulate user providing date/time)
    print("🗓️  Step 1: Scheduling appointment")
    response, updated_profile, next_step = await scheduling_service.collect_patient_info(
        "Tuesday morning", current_profile, current_step
    )
    print(f"Agent: {response}")
    print(f"Next step: {next_step.value}")
    print()
    
    current_step = next_step
    current_profile = updated_profile
    
    # Step 2: Start questionnaire
    print("📝 Step 2: Starting questionnaire")
    response, updated_profile, next_step = await scheduling_service.collect_patient_info(
        "ok", current_profile, current_step
    )
    print(f"Agent: {response}")
    print(f"Next step: {next_step.value}")
    print()
    
    current_step = next_step
    current_profile = updated_profile
    
    # Step 3: Answer questionnaire questions
    questionnaire_responses = [
        "United States",  # country
        "35",            # age
        "Male",          # gender
        "Diabetes",      # medical conditions
        "Metformin",     # medications
        "COVID-19 last month",  # recent events
        "2 years ago, gradually",  # hair loss onset
        "Crown area",    # hair loss location
        "Minoxidil, didn't work"  # previous treatments
    ]
    
    print("❓ Step 3: Answering questionnaire questions")
    for i, user_response in enumerate(questionnaire_responses, 1):
        print(f"User: {user_response}")
        response, updated_profile, next_step = await scheduling_service.collect_patient_info(
            user_response, current_profile, current_step
        )
        print(f"Agent: {response}")
        print(f"Next step: {next_step.value}")
        print()
        
        current_profile = updated_profile
        current_step = next_step
        
        # Check if questionnaire is complete
        if next_step == SchedulingStep.CLOSURE:
            break
    
    # Step 4: Show final results
    print("✅ Step 4: Questionnaire Complete!")
    print(f"📊 Total responses collected: {len(current_profile.questionnaire_responses)}")
    print()
    
    print("📋 Questionnaire Responses:")
    for response in current_profile.questionnaire_responses:
        status = "SKIPPED" if response.skipped else "ANSWERED"
        answer = response.answer if response.answer else "N/A"
        print(f"  • {response.question_id}: {answer} ({status})")
    
    print()
    print("🎉 Test completed successfully!")
    print(f"📈 Questionnaire step: {current_profile.questionnaire_step.value}")
    print(f"⏰ Completed at: {current_profile.questionnaire_completed_at}")


if __name__ == "__main__":
    asyncio.run(test_questionnaire_flow())
