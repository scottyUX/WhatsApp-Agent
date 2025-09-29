#!/usr/bin/env python3
"""
Test script for Anna - Istanbul Medic Consultation Assistant
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.specialized_agents.scheduling_agent import handle_scheduling_request

async def test_anna():
    """Test Anna's consultation scheduling capabilities."""
    print("Testing Anna - Istanbul Medic Consultation Assistant")
    print("=" * 60)
    print("Note: Intent detection is handled by the Manager Agent")
    print("Anna focuses solely on consultation scheduling")
    print("=" * 60)
    print("Testing Anna's Scheduling Responses:")
    
    # Test Anna's responses for different scenarios
    test_scenarios = [
        # New consultation scheduling
        {
            "name": "New Consultation",
            "messages": [
                "Hello, I'm interested in a consultation",
                "Yes, I'd like to schedule one",
                "My name is John Smith",
                "My phone is +1234567890",
                "My email is john@example.com",
                "Tuesday works for me",
                "Morning would be great",
                "2 PM sounds perfect"
            ]
        },
        # Appointment management
        {
            "name": "View Appointments",
            "messages": [
                "What appointments do I have?",
                "Show me my upcoming consultations"
            ]
        },
        {
            "name": "Reschedule Appointment",
            "messages": [
                "I need to reschedule my appointment",
                "Can I change my consultation time?",
                "I want to move my appointment to next week"
            ]
        },
        {
            "name": "Cancel Appointment",
            "messages": [
                "I need to cancel my consultation",
                "Can I cancel my appointment?",
                "I want to cancel my meeting"
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n--- Testing {scenario['name']} ---")
        for i, message in enumerate(scenario['messages'], 1):
            print(f"\nMessage {i}: {message}")
            try:
                response = await handle_scheduling_request(message, f"user_{i}")
                print(f"Anna: {response}")
            except Exception as e:
                print(f"Error: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_anna())
