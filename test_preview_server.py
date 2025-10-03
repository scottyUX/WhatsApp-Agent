#!/usr/bin/env python3
"""
Preview Server Testing Script
Tests the deployed preview server endpoints
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List

class PreviewServerTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
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
    
    async def test_chat_endpoint(self, message: str) -> bool:
        """Test the chat endpoint"""
        print(f"\n💬 Testing Chat Endpoint with message: '{message}'")
        try:
            payload = {
                "content": message,
                "media_urls": [],
                "audio_urls": []
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Chat endpoint passed: {data['content'][:100]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Chat endpoint failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Chat endpoint error: {e}")
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
                    print(f"✅ Webhook endpoint passed: {response_text[:100]}...")
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
                    print(f"✅ WhatsApp webhook endpoint passed: {response_text[:100]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ WhatsApp webhook endpoint failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ WhatsApp webhook endpoint error: {e}")
            return False

async def test_preview_server(base_url: str):
    """Test the preview server with comprehensive scenarios"""
    print(f"🚀 Testing Preview Server: {base_url}")
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
    
    async with PreviewServerTester(base_url) as tester:
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
        
        # Test 4: Webhook endpoint with different messages
        webhook_results = []
        for message in test_messages:
            result = await tester.test_webhook_endpoint(message)
            webhook_results.append(result)
            await asyncio.sleep(1)  # Rate limiting
        results['webhook_endpoint'] = all(webhook_results)
        
        # Test 5: WhatsApp webhook endpoint
        whatsapp_results = []
        for message in test_messages:
            result = await tester.test_whatsapp_webhook_endpoint(message)
            whatsapp_results.append(result)
            await asyncio.sleep(1)  # Rate limiting
        results['whatsapp_webhook'] = all(whatsapp_results)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PREVIEW SERVER TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL PREVIEW SERVER TESTS PASSED!")
        print("\n📋 Your preview server is ready for:")
        print("1. Real WhatsApp testing")
        print("2. Stakeholder review")
        print("3. Production deployment")
    else:
        print("\n⚠️  SOME PREVIEW SERVER TESTS FAILED!")
        print("Please check the errors above and fix any issues before proceeding.")
    
    return all_passed

def main():
    """Main function to run preview server tests"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python test_preview_server.py <preview_url>")
        print("Example: python test_preview_server.py https://whatsapp-agent-preview.vercel.app")
        sys.exit(1)
    
    preview_url = sys.argv[1]
    
    # Run the tests
    success = asyncio.run(test_preview_server(preview_url))
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
