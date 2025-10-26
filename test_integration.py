#!/usr/bin/env python3
"""
Simple integration test for Cal.com booking flow.

This tests the actual ConsultationService with a real database connection.
"""

import json
import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_booking_flow():
    """Test the booking flow with real database."""
    print("🧪 Testing Cal.com Booking Flow Integration...")
    
    try:
        from app.services.consultation_service import ConsultationService
        from app.database.db import SessionLocal
        
        # Create database session
        db = SessionLocal()
        
        # Create service
        service = ConsultationService(db)
        
        # Sample Cal.com webhook payload
        sample_payload = {
            "type": "BOOKING_CREATED",
            "data": {
                "id": f"test_booking_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "title": "Hair Transplant Consultation",
                "description": "Test consultation for booking flow",
                "startTime": "2025-10-26T15:00:00Z",
                "endTime": "2025-10-26T15:15:00Z",
                "status": "scheduled",
                "attendees": [
                    {
                        "name": "Test Patient",
                        "email": "test.patient@example.com",
                        "timeZone": "America/New_York"
                    }
                ],
                "responses": {
                    "phone": "+1-555-999-8888",
                    "location": "New York, NY"
                }
            }
        }
        
        print(f"📋 Testing with payload: {json.dumps(sample_payload, indent=2)}")
        
        # Process the webhook
        result = service.process_cal_webhook(sample_payload)
        
        print(f"✅ Result: {json.dumps(result, indent=2)}")
        
        # Check if user and patient profile were created
        if result.get("success"):
            print("\n🎉 SUCCESS! Booking flow completed successfully!")
            print(f"   - User created: {result.get('user_created', False)}")
            print(f"   - Patient profile created: {result.get('patient_profile_created', False)}")
            print(f"   - Phone captured: {result.get('attendee_phone_captured', False)}")
            print(f"   - Location captured: {result.get('attendee_location_captured', False)}")
        else:
            print(f"❌ FAILED: {result.get('message', 'Unknown error')}")
        
        # Clean up
        db.close()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the WhatsApp-Agent directory")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_booking_flow()
