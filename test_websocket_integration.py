#!/usr/bin/env python3
"""
Test script for WebSocket integration and Cal.com webhook
Tests real-time chat notifications for booking confirmations
"""

import asyncio
import json
import websockets
import requests
import time
from datetime import datetime

# Test configuration
BACKEND_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000/chat/ws"
TEST_USER_ID = "test_user_123"

async def test_websocket_connection():
    """Test WebSocket connection and message handling"""
    print("🔌 Testing WebSocket connection...")
    
    try:
        # Connect to WebSocket
        websocket_url = f"{WEBSOCKET_URL}/{TEST_USER_ID}"
        print(f"Connecting to: {websocket_url}")
        
        async with websockets.connect(websocket_url) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a test message
            test_message = "Hello from test client"
            await websocket.send(test_message)
            print(f"📤 Sent: {test_message}")
            
            # Wait for echo response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 Received: {response}")
            
            # Keep connection alive for webhook test
            print("🔄 Keeping connection alive for webhook test...")
            await asyncio.sleep(2)
            
    except asyncio.TimeoutError:
        print("❌ WebSocket connection timed out")
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

def test_cal_webhook():
    """Test Cal.com webhook with sample booking data"""
    print("\n📅 Testing Cal.com webhook...")
    
    # Sample Cal.com webhook payload
    webhook_payload = {
        "type": "BOOKING_CREATED",
        "data": {
            "id": "test_booking_12345",
            "title": "Free Consultation",
            "startTime": "2025-10-10T10:00:00Z",
            "endTime": "2025-10-10T10:15:00Z",
            "attendees": [
                {
                    "name": "John Doe",
                    "email": "john.doe@example.com"
                }
            ]
        }
    }
    
    try:
        # Send webhook request
        webhook_url = f"{BACKEND_URL}/api/cal-webhook"
        print(f"Sending webhook to: {webhook_url}")
        print(f"Payload: {json.dumps(webhook_payload, indent=2)}")
        
        response = requests.post(
            webhook_url,
            json=webhook_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📤 Webhook response status: {response.status_code}")
        print(f"📥 Webhook response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook processed successfully!")
        else:
            print("❌ Webhook failed!")
            
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")

async def test_websocket_manager():
    """Test WebSocket manager functionality"""
    print("\n🔧 Testing WebSocket manager...")
    
    try:
        from app.services.websocket_manager import manager
        
        # Test booking data
        booking_data = {
            "id": "test_booking_67890",
            "title": "Test Consultation",
            "startTime": "2025-10-10T14:00:00Z",
            "attendee_name": "Jane Smith",
            "attendee_email": "jane.smith@example.com"
        }
        
        print(f"Booking data: {booking_data}")
        print(f"Connected users: {manager.get_connected_users()}")
        print(f"Connection count: {manager.get_connection_count()}")
        
        # Test sending booking confirmation (will fail if no connections)
        if manager.get_connection_count() > 0:
            for user_id in manager.get_connected_users():
                success = await manager.send_booking_confirmation(user_id, booking_data)
                print(f"📤 Sent confirmation to {user_id}: {success}")
        else:
            print("⚠️ No connected users to test with")
            
    except Exception as e:
        print(f"❌ WebSocket manager test failed: {e}")

async def test_full_integration():
    """Test full integration: WebSocket + Webhook"""
    print("\n🚀 Testing full integration...")
    
    # Start WebSocket connection in background
    websocket_task = asyncio.create_task(test_websocket_connection())
    
    # Wait a bit for connection to establish
    await asyncio.sleep(1)
    
    # Test webhook (this should send notification to WebSocket)
    test_cal_webhook()
    
    # Wait for WebSocket to finish
    await websocket_task

def test_backend_health():
    """Test if backend is running and healthy"""
    print("🏥 Testing backend health...")
    
    try:
        # Test health endpoint
        health_url = f"{BACKEND_URL}/health"
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Backend is healthy!")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend is not running: {e}")
        print("💡 Make sure to start the backend with: python -m uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload")
        return False

async def main():
    """Run all tests"""
    print("🧪 Starting WebSocket Integration Tests")
    print("=" * 50)
    
    # Test backend health first
    if not test_backend_health():
        return
    
    # Test WebSocket manager
    await test_websocket_manager()
    
    # Test full integration
    await test_full_integration()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
