#!/usr/bin/env python3
"""
Test script for the simplified knowledge-only agent
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.simple_manager_agent import run_simple_manager

async def test_simple_agent():
    """Test the simplified agent with basic questions"""
    
    print("🧪 Testing Simplified Knowledge Agent")
    print("=" * 50)
    
    # Test questions
    test_questions = [
        "What is Istanbul Medic?",
        "Do you offer hair transplant procedures?",
        "How much does a hair transplant cost?",
        "Where are you located?",
        "How can I book a consultation?"
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
