#!/usr/bin/env python3
"""
Test script for the updated Manager Agent with scheduling intent detection
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from agents.manager_agent import run_manager, detect_scheduling_intent

async def test_manager_agent():
    """Test the manager agent with scheduling intent detection."""
    print("Testing Manager Agent with Scheduling Intent Detection")
    print("=" * 60)
    
    # Test scheduling intent detection
    test_messages = [
        ("I'd like to schedule a consultation", True),
        ("Can I book an appointment?", True),
        ("I want to speak with a specialist", True),
        ("Schedule a call with the doctor", True),
        ("Book a free consultation", True),
        ("What treatments do you offer?", False),
        ("I need help with hair loss", False),
        ("How much does it cost?", False),
        ("Tell me about your services", False),
    ]
    
    print("Testing Intent Detection:")
    for message, expected in test_messages:
        is_scheduling = await detect_scheduling_intent(message)
        status = "CORRECT" if is_scheduling == expected else "WRONG"
        print(f"  '{message}' → {is_scheduling} ({status})")
    
    print("\n" + "=" * 60)
    print("Testing Manager Agent Routing:")
    
    # Test manager agent routing
    test_conversations = [
        ("I'd like to schedule a consultation", "Should route to Anna"),
        ("What treatments do you offer?", "Should route to language agent"),
        ("I need help with hair loss", "Should route to language agent"),
        ("Can I book an appointment?", "Should route to Anna"),
    ]
    
    for message, expected_route in test_conversations:
        print(f"\nMessage: {message}")
        print(f"Expected: {expected_route}")
        try:
            response = await run_manager(message, "test_user_123")
            print(f"Response: {response[:100]}...")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_manager_agent())
