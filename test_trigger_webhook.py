#!/usr/bin/env python3
"""
Trigger Cal.com webhook to test real-time notifications
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8000"

def trigger_booking_webhook():
    """Trigger a Cal.com booking webhook"""
    print("📅 Triggering Cal.com booking webhook...")
    
    # Sample booking data
    webhook_payload = {
        "type": "BOOKING_CREATED",
        "data": {
            "id": f"booking_{int(time.time())}",
            "title": "Free Consultation",
            "startTime": "2025-10-10T15:00:00Z",
            "endTime": "2025-10-10T15:15:00Z",
            "attendees": [
                {
                    "name": "Alice Johnson",
                    "email": "alice.johnson@example.com"
                }
            ]
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/cal-webhook",
            json=webhook_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📤 Webhook status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook triggered successfully!")
            print("🔔 Check the WebSocket listener for real-time notification!")
        else:
            print("❌ Webhook failed!")
            
    except Exception as e:
        print(f"❌ Failed to trigger webhook: {e}")

if __name__ == "__main__":
    print("🚀 Cal.com Webhook Trigger")
    print("=" * 30)
    trigger_booking_webhook()
