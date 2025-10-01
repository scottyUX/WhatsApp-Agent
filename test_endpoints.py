#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing Script for WhatsApp Agent
Tests all available endpoints with various scenarios
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000"

class EndpointTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self) -> bool:
        """Test the health check endpoint"""
        print("🏥 Testing Health Check...")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_webhook_verification(self) -> bool:
        """Test webhook verification endpoint"""
        print("\n🔗 Testing Webhook Verification...")
        try:
            async with self.session.get(f"{self.base_url}/api/webhook") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Webhook verification passed: {data}")
                    return True
                else:
                    print(f"❌ Webhook verification failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Webhook verification error: {e}")
            return False
    
    async def test_chat_endpoint(self, message: str, media_urls: List[str] = None, audio_urls: List[str] = None) -> bool:
        """Test the chat endpoint"""
        print(f"\n💬 Testing Chat Endpoint with message: '{message}'")
        try:
            payload = {
                "content": message,
                "media_urls": media_urls or [],
                "audio_urls": audio_urls or []
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Chat endpoint passed: {data}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Chat endpoint failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Chat endpoint error: {e}")
            return False
    
    async def test_chat_stream_endpoint(self, message: str) -> bool:
        """Test the chat streaming endpoint"""
        print(f"\n🌊 Testing Chat Stream Endpoint with message: '{message}'")
        try:
            payload = {
                "content": message,
                "media_urls": [],
                "audio_urls": []
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/stream",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    print("✅ Chat stream endpoint connected")
                    # Read streaming response
                    async for chunk in response.content.iter_chunked(1024):
                        if chunk:
                            print(f"📦 Stream chunk: {chunk.decode('utf-8', errors='ignore')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Chat stream endpoint failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Chat stream endpoint error: {e}")
            return False
    
    async def test_webhook_endpoint(self, message: str, phone_number: str = "+1234567890") -> bool:
        """Test the webhook endpoint with form data"""
        print(f"\n📱 Testing Webhook Endpoint with message: '{message}'")
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('Body', message)
            form_data.add_field('From', phone_number)
            form_data.add_field('To', '+15551234567')
            form_data.add_field('MessageSid', 'test_message_sid')
            
            async with self.session.post(f"{self.base_url}/api/webhook", data=form_data) as response:
                if response.status == 200:
                    response_text = await response.text()
                    print(f"✅ Webhook endpoint passed: {response_text[:200]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Webhook endpoint failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Webhook endpoint error: {e}")
            return False
    
    async def test_whatsapp_webhook_endpoint(self, message: str, phone_number: str = "+1234567890") -> bool:
        """Test the WhatsApp webhook endpoint"""
        print(f"\n📲 Testing WhatsApp Webhook Endpoint with message: '{message}'")
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('Body', message)
            form_data.add_field('From', phone_number)
            form_data.add_field('To', '+15551234567')
            form_data.add_field('MessageSid', 'test_message_sid')
            
            async with self.session.post(f"{self.base_url}/whatsapp/webhook", data=form_data) as response:
                if response.status == 200:
                    response_text = await response.text()
                    print(f"✅ WhatsApp webhook endpoint passed: {response_text[:200]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ WhatsApp webhook endpoint failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ WhatsApp webhook endpoint error: {e}")
            return False
    
    async def test_agent_endpoint(self) -> bool:
        """Test the agent test endpoint (only available in DEBUG mode)"""
        print("\n🤖 Testing Agent Endpoint...")
        try:
            async with self.session.get(f"{self.base_url}/test/agent") as response:
                if response.status == 200:
                    response_text = await response.text()
                    print(f"✅ Agent endpoint passed: {response_text[:200]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Agent endpoint failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Agent endpoint error: {e}")
            return False
    
    async def test_message_endpoint(self) -> bool:
        """Test the message test endpoint (only available in DEBUG mode)"""
        print("\n📤 Testing Message Endpoint...")
        try:
            async with self.session.get(f"{self.base_url}/test/message") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Message endpoint passed: {data}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Message endpoint failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Message endpoint error: {e}")
            return False

async def run_comprehensive_tests():
    """Run all endpoint tests"""
    print("🚀 Starting Comprehensive Endpoint Testing")
    print("=" * 60)
    
    # Test scenarios
    test_messages = [
        "Hello, I want to schedule an appointment",
        "I'm interested in hair transplantation",
        "What are your services?",
        "I need to cancel my appointment",
        "What is my email address?"
    ]
    
    results = {}
    
    async with EndpointTester() as tester:
        # Test 1: Health check
        results['health_check'] = await tester.test_health_check()
        
        # Test 2: Webhook verification
        results['webhook_verification'] = await tester.test_webhook_verification()
        
        # Test 3: Chat endpoint with different messages
        chat_results = []
        for message in test_messages:
            result = await tester.test_chat_endpoint(message)
            chat_results.append(result)
            await asyncio.sleep(1)  # Rate limiting
        results['chat_endpoint'] = all(chat_results)
        
        # Test 4: Chat stream endpoint
        results['chat_stream'] = await tester.test_chat_stream_endpoint("Hello, I want to schedule an appointment")
        
        # Test 5: Webhook endpoint with different messages
        webhook_results = []
        for message in test_messages:
            result = await tester.test_webhook_endpoint(message)
            webhook_results.append(result)
            await asyncio.sleep(1)  # Rate limiting
        results['webhook_endpoint'] = all(webhook_results)
        
        # Test 6: WhatsApp webhook endpoint
        whatsapp_results = []
        for message in test_messages:
            result = await tester.test_whatsapp_webhook_endpoint(message)
            whatsapp_results.append(result)
            await asyncio.sleep(1)  # Rate limiting
        results['whatsapp_webhook'] = all(whatsapp_results)
        
        # Test 7: Agent endpoint (DEBUG mode only)
        results['agent_endpoint'] = await tester.test_agent_endpoint()
        
        # Test 8: Message endpoint (DEBUG mode only)
        results['message_endpoint'] = await tester.test_message_endpoint()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL ENDPOINT TESTS PASSED!")
        print("\n📋 Your endpoints are working correctly. You can now:")
        print("1. Test with real WhatsApp messages")
        print("2. Test with real Twilio webhooks")
        print("3. Test the chat interface")
        print("4. Deploy to production")
    else:
        print("\n⚠️  SOME ENDPOINT TESTS FAILED!")
        print("Please check the errors above and fix any issues.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
