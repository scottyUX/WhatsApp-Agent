#!/usr/bin/env python3
"""
Test script for the simplified knowledge-only agent
"""

import asyncio
import sys
import os

import pytest

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.simple_manager_agent import run_simple_manager

pytestmark = pytest.mark.skip(reason="Integration script for manual execution; skipped in automated test suite.")

async def test_simple_agent():
    """Test the simplified agent with basic questions"""
    
    print("🧪 Testing Istanbul Medic Consultant Agent")
    print("=" * 50)
    
    # Test questions to verify vector store integration and specialized expertise
    test_questions = [
        "What is Istanbul Medic and what services do you offer?",
        "What hair transplant techniques do you use?",
        "How much does a hair transplant cost?",
        "Where are your clinics located?",
        "How can I book a free consultation?",
        "What are your hair transplant packages and what's included?",
        "Do you have before and after photos I can see?",
        "What is the recovery time for hair transplant?",
        "Do you offer financing options?",
        "What makes Istanbul Medic different from other clinics?",
        "What is FUE hair transplant and how does it work?",
        "Am I a good candidate for hair transplant?",
        "How many grafts do I need for my hair loss?",
        "What should I expect during the consultation?",
        "Do you help with travel arrangements to Turkey?",
        "Is it safe to have surgery in Turkey?",
        "What certifications do your surgeons have?",
        "How long do I need to stay in Istanbul?",
        "What happens if I'm not satisfied with results?",
        "Can you help me understand the hair transplant process?"
    ]
    
    context = {
        "user_id": "test_user",
        "channel": "chat"
    }
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n❓ Question {i}: {question}")
        print("-" * 30)
        
        try:
            response = await run_simple_manager(question, context, None)
            print(f"✅ Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_simple_agent())
