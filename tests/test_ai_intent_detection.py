#!/usr/bin/env python3
"""
Test script to demonstrate AI-based intent detection vs keyword-based
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.agents.manager_agent import detect_scheduling_intent

async def test_ai_intent_detection():
    """Test AI-based intent detection with nuanced examples."""
    print("Testing AI-Based Intent Detection")
    print("=" * 60)
    print("This demonstrates how AI can understand context and nuance")
    print("better than simple keyword matching.")
    print("=" * 60)
    
    # Test cases that show the difference between keyword and AI detection
    test_cases = [
        # Clear scheduling intent
        ("I'd like to schedule a consultation", True, "Clear scheduling request"),
        ("Can I book an appointment with a specialist?", True, "Direct appointment booking"),
        ("I want to speak with a doctor about my hair loss", True, "Want to speak with doctor"),
        ("When can I meet with someone about treatment options?", True, "Asking about meeting"),
        
        # Ambiguous cases that AI should handle better
        ("I'm interested in your services and would like to know more", False, "General interest, not scheduling"),
        ("What time do you close?", False, "Business hours question"),
        ("I have a question about scheduling", True, "Question about scheduling process"),
        ("Do you offer free consultations?", False, "Asking about service availability"),
        ("I need to reschedule my appointment", True, "Rescheduling request"),
        ("What are your consultation fees?", False, "Pricing question"),
        
        # Edge cases
        ("I'm looking for information about hair transplants", False, "Information seeking"),
        ("Can someone call me back?", True, "Request for callback/contact"),
        ("I'd like to discuss my options", True, "Want to discuss options"),
        ("What treatments do you offer?", False, "Treatment information request"),
        ("I'm not sure if I need a consultation", True, "Uncertain but interested in consultation"),
    ]
    
    print("Testing AI Intent Detection:")
    print("-" * 60)
    
    correct_predictions = 0
    total_predictions = len(test_cases)
    
    for message, expected, description in test_cases:
        try:
            is_scheduling = await detect_scheduling_intent(message)
            is_correct = is_scheduling == expected
            status = "✓ CORRECT" if is_correct else "✗ WRONG"
            
            if is_correct:
                correct_predictions += 1
            
            print(f"\nMessage: '{message}'")
            print(f"Description: {description}")
            print(f"Expected: {expected}")
            print(f"AI Result: {is_scheduling}")
            print(f"Status: {status}")
            
        except Exception as e:
            print(f"\nMessage: '{message}'")
            print(f"Error: {e}")
            print(f"Status: ✗ ERROR")
    
    accuracy = (correct_predictions / total_predictions) * 100
    print(f"\n" + "=" * 60)
    print(f"AI Intent Detection Accuracy: {accuracy:.1f}% ({correct_predictions}/{total_predictions})")
    print("=" * 60)
    
    print("\nBenefits of AI-based intent detection:")
    print("• Understands context and nuance")
    print("• Handles ambiguous language")
    print("• Reduces false positives/negatives")
    print("• Adapts to different phrasings")
    print("• More natural conversation flow")

if __name__ == "__main__":
    asyncio.run(test_ai_intent_detection())

