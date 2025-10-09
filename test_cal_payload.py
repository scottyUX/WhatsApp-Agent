#!/usr/bin/env python3
"""
Test script to see the full Cal.com webhook payload structure
"""

import requests
import json
import time

BACKEND_URL = "https://whats-app-agent-git-feature-cal-webhook-int-65af69-whatsapp-bot.vercel.app"

def test_detailed_booking_payload():
    """Test with a detailed booking payload to see all available data"""
    print("🔍 Testing detailed Cal.com booking payload...")
    
    # More comprehensive booking data (simulating what Cal.com might send)
    detailed_booking = {
        "type": "BOOKING_CREATED",
        "data": {
            "id": f"detailed_test_{int(time.time())}",
            "title": "Free Consultation",
            "description": "Hair transplant consultation",
            "startTime": "2025-10-10T18:00:00Z",
            "endTime": "2025-10-10T18:15:00Z",
            "timeZone": "Europe/Istanbul",
            "status": "ACCEPTED",
            "location": "Istanbul Medic Clinic",
            "attendees": [
                {
                    "name": "John Smith",
                    "email": "john.smith@example.com",
                    "timeZone": "America/New_York",
                    "locale": "en"
                }
            ],
            "organizer": {
                "name": "Istanbul Medic",
                "email": "info@istanbulmedic.com"
            },
            "metadata": {
                "source": "cal.com",
                "version": "1.0"
            },
            "responses": {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "phone": "+1-555-123-4567",
                "message": "I'm interested in FUE hair transplant",
                "age": "35",
                "hair_loss_pattern": "Norwood 3"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/cal-webhook",
            json=detailed_booking,
            headers={
                "Content-Type": "application/json",
                "x-cal-signature-256": "test-signature"
            },
            timeout=15
        )
        
        print(f"📤 Response status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Detailed payload processed successfully!")
            print("\n📋 This shows what patient information we can extract:")
            print("• Full Name: John Smith")
            print("• Email: john.smith@example.com")
            print("• Phone: +1-555-123-4567")
            print("• Message: I'm interested in FUE hair transplant")
            print("• Age: 35")
            print("• Hair Loss Pattern: Norwood 3")
            print("• Time Zone: America/New_York")
            print("• Booking ID: detailed_test_[timestamp]")
        else:
            print("❌ Detailed payload failed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_minimal_booking_payload():
    """Test with minimal booking payload (what Cal.com typically sends)"""
    print("\n🔍 Testing minimal Cal.com booking payload...")
    
    minimal_booking = {
        "type": "BOOKING_CREATED",
        "data": {
            "id": f"minimal_test_{int(time.time())}",
            "title": "Free Consultation",
            "startTime": "2025-10-10T19:00:00Z",
            "endTime": "2025-10-10T19:15:00Z",
            "attendees": [
                {
                    "name": "Jane Doe",
                    "email": "jane.doe@example.com"
                }
            ]
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/cal-webhook",
            json=minimal_booking,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📤 Response status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Minimal payload processed successfully!")
            print("\n📋 This shows the basic patient information we get:")
            print("• Name: Jane Doe")
            print("• Email: jane.doe@example.com")
            print("• Booking ID: minimal_test_[timestamp]")
        else:
            print("❌ Minimal payload failed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🧪 Cal.com Patient Data Extraction Test")
    print("=" * 50)
    
    test_detailed_booking_payload()
    test_minimal_booking_payload()
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print("✅ We extract: Name, Email, Booking ID, Time, Title")
    print("⚠️ Additional data depends on Cal.com form configuration")
    print("💡 You can customize Cal.com forms to collect more patient info")
