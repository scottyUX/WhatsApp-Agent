#!/usr/bin/env python3
"""
Real-time WebSocket test - listens for booking confirmations
"""

import asyncio
import websockets
import json
import requests
import time

WEBSOCKET_URL = "ws://localhost:8000/chat/ws"
TEST_USER_ID = "realtime_test_user"

async def listen_for_notifications():
    """Listen for real-time booking notifications"""
    print(f"🔌 Connecting to WebSocket as user: {TEST_USER_ID}")
    
    try:
        websocket_url = f"{WEBSOCKET_URL}/{TEST_USER_ID}"
        async with websockets.connect(websocket_url) as websocket:
            print("✅ Connected! Listening for booking notifications...")
            print("💡 In another terminal, run: python test_trigger_webhook.py")
            print("⏳ Waiting for notifications...\n")
            
            while True:
                try:
                    # Wait for messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    
                    # Parse the message
                    try:
                        data = json.loads(message)
                        if data.get("type") == "booking_confirmation":
                            print("🎉 BOOKING CONFIRMATION RECEIVED!")
                            print("=" * 50)
                            booking_data = data.get("data", {})
                            print(f"📅 Event: {booking_data.get('title', 'N/A')}")
                            print(f"👤 Attendee: {booking_data.get('attendee_name', 'N/A')}")
                            print(f"📧 Email: {booking_data.get('attendee_email', 'N/A')}")
                            print(f"🕐 Time: {booking_data.get('start_time', 'N/A')}")
                            print(f"🆔 Booking ID: {booking_data.get('booking_id', 'N/A')}")
                            print("=" * 50)
                            print(f"💬 Message:\n{booking_data.get('message', 'N/A')}")
                            print("=" * 50)
                        else:
                            print(f"📥 Received: {message}")
                    except json.JSONDecodeError:
                        print(f"📥 Received (text): {message}")
                        
                except asyncio.TimeoutError:
                    print("⏰ No messages received in 30 seconds...")
                    print("💡 Run the webhook trigger script to test notifications")
                    
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

if __name__ == "__main__":
    print("🧪 Real-time WebSocket Notification Listener")
    print("=" * 50)
    asyncio.run(listen_for_notifications())
