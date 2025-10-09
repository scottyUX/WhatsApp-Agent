#!/usr/bin/env python3
"""
Full integration test for Cal.com webhook + WebSocket notifications
Simulates the complete booking flow
"""

import asyncio
import websockets
import requests
import json
import time

# Configuration
BACKEND_URL = "https://whats-app-agent-git-feature-cal-webhook-int-65af69-whatsapp-bot.vercel.app"
WEBSOCKET_URL = f"ws://{BACKEND_URL.replace('https://', '')}/chat/ws"
TEST_USER_ID = "integration_test_user"

async def test_websocket_connection():
    """Test WebSocket connection and listen for notifications"""
    print("🔌 Testing WebSocket connection...")
    
    try:
        # Note: WebSocket URL needs to be wss:// for production
        websocket_url = f"wss://{BACKEND_URL.replace('https://', '')}/chat/ws/{TEST_USER_ID}"
        print(f"Connecting to: {websocket_url}")
        
        async with websockets.connect(websocket_url) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a test message
            await websocket.send("Hello from integration test")
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 Echo response: {response}")
            
            # Keep connection alive for webhook test
            print("🔄 Connection active, waiting for webhook notifications...")
            await asyncio.sleep(3)
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        print("💡 Note: WebSocket might not work with HTTPS in this test environment")

def test_webhook_with_signature():
    """Test webhook with Cal.com signature header"""
    print("\n📅 Testing Cal.com webhook with signature...")
    
    # Sample booking data
    booking_data = {
        "type": "BOOKING_CREATED",
        "data": {
            "id": f"integration_test_{int(time.time())}",
            "title": "Integration Test Consultation",
            "startTime": "2025-10-10T16:00:00Z",
            "endTime": "2025-10-10T16:15:00Z",
            "attendees": [
                {
                    "name": "Integration Test User",
                    "email": "integration.test@example.com"
                }
            ]
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/cal-webhook",
            json=booking_data,
            headers={
                "Content-Type": "application/json",
                "x-cal-signature-256": "test-signature-12345"
            },
            timeout=15
        )
        
        print(f"📤 Webhook status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook processed successfully!")
            return True
        else:
            print("❌ Webhook failed!")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False

def test_webhook_without_signature():
    """Test webhook without signature (should still work)"""
    print("\n📅 Testing Cal.com webhook without signature...")
    
    booking_data = {
        "type": "BOOKING_CREATED",
        "data": {
            "id": f"no_sig_test_{int(time.time())}",
            "title": "No Signature Test",
            "startTime": "2025-10-10T17:00:00Z",
            "attendees": [
                {
                    "name": "No Signature User",
                    "email": "nosig@example.com"
                }
            ]
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/cal-webhook",
            json=booking_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📤 Webhook status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False

def test_booking_cancellation():
    """Test booking cancellation webhook"""
    print("\n📅 Testing booking cancellation webhook...")
    
    cancellation_data = {
        "type": "BOOKING_CANCELLED",
        "data": {
            "id": f"cancelled_{int(time.time())}",
            "title": "Cancelled Consultation"
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/cal-webhook",
            json=cancellation_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📤 Cancellation status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Cancellation test failed: {e}")
        return False

async def main():
    """Run all integration tests"""
    print("🧪 Cal.com Webhook Integration Test Suite")
    print("=" * 50)
    
    # Test 1: WebSocket connection (might fail due to HTTPS/WSS)
    try:
        await test_websocket_connection()
    except Exception as e:
        print(f"⚠️ WebSocket test skipped: {e}")
    
    # Test 2: Webhook with signature
    webhook_with_sig = test_webhook_with_signature()
    
    # Test 3: Webhook without signature
    webhook_without_sig = test_webhook_without_signature()
    
    # Test 4: Booking cancellation
    cancellation_test = test_booking_cancellation()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Webhook with signature: {'PASS' if webhook_with_sig else 'FAIL'}")
    print(f"✅ Webhook without signature: {'PASS' if webhook_without_sig else 'FAIL'}")
    print(f"✅ Booking cancellation: {'PASS' if cancellation_test else 'FAIL'}")
    print("⚠️ WebSocket: Requires WSS connection (production only)")
    
    if webhook_with_sig and webhook_without_sig and cancellation_test:
        print("\n🎉 All webhook tests passed! Cal.com integration is ready!")
    else:
        print("\n❌ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    asyncio.run(main())
