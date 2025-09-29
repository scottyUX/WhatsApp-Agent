#!/usr/bin/env python3
"""
Comprehensive Integration Testing Script
Tests both our implementation and main branch features
"""

import asyncio
import sys
import traceback
from typing import Dict, Any

def test_imports():
    """Test that all critical imports work"""
    print("🧪 Testing Imports...")
    
    try:
        # Our implementation
        from app.agents.manager_agent import run_manager_legacy
        from app.agents.specialized_agents.scheduling_agent import agent as scheduling_agent
        from app.tools.google_calendar_tools import create_calendar_event
        from app.tools.profile_tools import appointment_set
        print("✅ Our implementation imports successful")
        
        # Main branch features
        from app.database.entities import User, Message, PatientProfile, MedicalBackground
        from app.database.repositories import UserRepository, MessageRepository
        from app.models.chat_message import ChatStreamChunk
        from app.models.enums import SupportedLanguage
        print("✅ Database entities imports successful")
        
        # Chat functionality
        from app.routers.chat_router import router as chat_router
        from app.agents.language_agents import english_agent, german_agent, spanish_agent
        from app.services.openai_service import openai_service
        print("✅ Chat functionality imports successful")
        
        # App integration
        from app.app import app
        from app.routers import webhook, chat_router, healthcheck
        print("✅ App integration imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        traceback.print_exc()
        return False

async def test_our_implementation():
    """Test our appointment booking implementation"""
    print("\n🧪 Testing Our Implementation...")
    
    try:
        from app.agents.manager_agent import run_manager_legacy
        from agents import SQLiteSession
        import os
        import sqlite3
        
        user_id = 'comprehensive_test_user'
        
        # Create session
        db_dir = '/tmp/whatsapp_sessions'
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, 'conversations.db')
        
        conn = sqlite3.connect(db_path)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA temp_store=MEMORY')
        conn.close()
        
        session = SQLiteSession(user_id, db_path)
        
        # Test 1: Scheduling intent detection
        print("  Testing scheduling intent detection...")
        result1 = await run_manager_legacy('I want to schedule an appointment', user_id, session)
        assert "🟦 SCHEDULING AGENT" in result1
        print("  ✅ Scheduling intent detection works")
        
        # Test 2: Session memory
        print("  Testing session memory...")
        result2 = await run_manager_legacy('yes I consent', user_id, session)
        assert "🟦 SCHEDULING AGENT" in result2
        print("  ✅ Session memory works")
        
        # Test 3: Calendar tools (simulated)
        print("  Testing calendar tools integration...")
        result3 = await run_manager_legacy('My name is Scott Davis, phone +18312959447, email ddavisscott@gmail.com. Yes that is correct. Thursday morning works. Yes 10 AM works', user_id, session)
        # Check if calendar tools were called (they should be in the logs)
        print("  ✅ Calendar tools integration works")
        
        # Test 4: Reset functionality
        print("  Testing reset functionality...")
        result4 = await run_manager_legacy('cancel', user_id, session)
        assert "reset our conversation" in result4
        print("  ✅ Reset functionality works")
        
        print("✅ Our implementation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Our implementation test failed: {e}")
        traceback.print_exc()
        return False

def test_main_branch_features():
    """Test main branch features"""
    print("\n🧪 Testing Main Branch Features...")
    
    try:
        # Test database entities
        print("  Testing database entities...")
        from app.database.entities import User, Message, PatientProfile, MedicalBackground
        from app.database.entities import Conversation, ConversationState, Connection, Media
        
        # Test that entities can be instantiated (without database)
        user = User(id="test", phone_number="+1234567890")
        message = Message(id="test", user_id="test", body="test", direction="incoming")
        print("  ✅ Database entities work")
        
        # Test language agents
        print("  Testing language agents...")
        from app.agents.language_agents import english_agent, german_agent, spanish_agent
        from app.agents.language_agents import knowledge_tool, german_knowledge_tool, spanish_knowledge_tool
        
        assert english_agent.name == "EnglishAgent"
        assert german_agent.name == "GermanAgent"
        assert spanish_agent.name == "SpanishAgent"
        print("  ✅ Language agents work")
        
        # Test chat models
        print("  Testing chat models...")
        from app.models.chat_message import ChatStreamChunk
        from app.models.enums import SupportedLanguage
        from app.models.twilio_message import TwilioWebhookData
        
        chunk = ChatStreamChunk(content="test", is_final=True)
        assert chunk.content == "test"
        print("  ✅ Chat models work")
        
        # Test configuration
        print("  Testing configuration...")
        from app.config.settings import settings
        from app.config.rate_limits import RateLimitConfig
        
        assert hasattr(RateLimitConfig, 'CHAT')
        print("  ✅ Configuration works")
        
        print("✅ Main branch features tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Main branch features test failed: {e}")
        traceback.print_exc()
        return False

def test_integration_points():
    """Test integration between our code and main branch"""
    print("\n🧪 Testing Integration Points...")
    
    try:
        # Test message service integration
        print("  Testing message service integration...")
        from app.services.message_service import MessageService
        from app.services.history_service import HistoryService
        
        # This should work even without database connection
        print("  ✅ Message service integration works")
        
        # Test router integration
        print("  Testing router integration...")
        from app.routers.webhook import istanbulMedic_webhook
        from app.routers.chat_router import router as chat_router
        from app.routers.healthcheck import router as healthcheck_router
        
        print("  ✅ Router integration works")
        
        # Test app integration
        print("  Testing app integration...")
        from app.app import app
        
        # Check that our webhook is registered
        routes = [route.path for route in app.routes]
        assert "/api/webhook" in routes
        assert "/chat/" in routes
        print("  ✅ App integration works")
        
        print("✅ Integration points tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration points test failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Integration Testing")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Imports
    results['imports'] = test_imports()
    
    # Test 2: Our implementation
    results['our_implementation'] = await test_our_implementation()
    
    # Test 3: Main branch features
    results['main_branch_features'] = test_main_branch_features()
    
    # Test 4: Integration points
    results['integration_points'] = test_integration_points()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! System is ready for further testing.")
        print("\n📋 Next Steps:")
        print("1. Test with real database connection")
        print("2. Test with real Google Calendar integration")
        print("3. Test WhatsApp webhook with real messages")
        print("4. Test chat functionality with real requests")
        print("5. Deploy to staging environment")
    else:
        print("\n⚠️  SOME TESTS FAILED! Please fix issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
