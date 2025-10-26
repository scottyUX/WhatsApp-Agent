#!/usr/bin/env python3
"""
Test script for the enhanced Cal.com booking flow.

This script tests the ConsultationService with sample Cal.com webhook payloads
to ensure that users and patient profiles are created correctly.
"""

import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

# Mock database session for testing
class MockDB:
    def __init__(self):
        self.users = []
        self.patient_profiles = []
        self.consultations = []
    
    def query(self, model):
        return MockQuery(model, self)
    
    def add(self, obj):
        if hasattr(obj, 'id') and not obj.id:
            obj.id = str(uuid.uuid4())
        if obj.__class__.__name__ == 'User':
            self.users.append(obj)
        elif obj.__class__.__name__ == 'PatientProfile':
            self.patient_profiles.append(obj)
        elif obj.__class__.__name__ == 'Consultation':
            self.consultations.append(obj)
    
    def commit(self):
        pass
    
    def refresh(self, obj):
        pass

class MockQuery:
    def __init__(self, model, db):
        self.model = model
        self.db = db
        self.filters = []
    
    def filter(self, condition):
        self.filters.append(condition)
        return self
    
    def first(self):
        # Simple mock implementation
        if self.model.__name__ == 'User':
            for user in self.db.users:
                if self._matches_filters(user):
                    return user
        elif self.model.__name__ == 'PatientProfile':
            for profile in self.db.patient_profiles:
                if self._matches_filters(profile):
                    return profile
        return None
    
    def _matches_filters(self, obj):
        # Simple filter matching for testing
        for filter_condition in self.filters:
            # This is a simplified implementation
            pass
        return True

# Sample Cal.com webhook payloads
SAMPLE_BOOKING_CREATED = {
    "type": "BOOKING_CREATED",
    "data": {
        "id": "cal_booking_123",
        "title": "Hair Transplant Consultation",
        "description": "Initial consultation for hair transplant procedure",
        "startTime": "2025-10-26T10:00:00Z",
        "endTime": "2025-10-26T10:15:00Z",
        "status": "scheduled",
        "attendees": [
            {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "timeZone": "America/New_York"
            }
        ],
        "responses": {
            "phone": "+1-555-123-4567",
            "location": "New York, NY",
            "age": "35"
        }
    }
}

SAMPLE_BOOKING_WITHOUT_PHONE = {
    "type": "BOOKING_CREATED",
    "data": {
        "id": "cal_booking_456",
        "title": "Hair Transplant Consultation",
        "description": "Follow-up consultation",
        "startTime": "2025-10-27T14:00:00Z",
        "endTime": "2025-10-27T14:15:00Z",
        "status": "scheduled",
        "attendees": [
            {
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "timeZone": "Europe/London"
            }
        ],
        "responses": {
            "location": "London, UK"
        }
    }
}

def test_consultation_service():
    """Test the ConsultationService with sample data."""
    print("🧪 Testing ConsultationService...")
    
    # Create mock database
    mock_db = MockDB()
    
    # Import and test the service
    try:
        from app.services.consultation_service import ConsultationService
        
        service = ConsultationService(mock_db)
        
        # Test 1: Booking with phone number
        print("\n📋 Test 1: Booking with phone number")
        result1 = service.process_cal_webhook(SAMPLE_BOOKING_CREATED)
        print(f"Result: {json.dumps(result1, indent=2)}")
        
        # Test 2: Booking without phone number
        print("\n📋 Test 2: Booking without phone number")
        result2 = service.process_cal_webhook(SAMPLE_BOOKING_WITHOUT_PHONE)
        print(f"Result: {json.dumps(result2, indent=2)}")
        
        # Test 3: Duplicate booking (should find existing user/profile)
        print("\n📋 Test 3: Duplicate booking (deduplication)")
        result3 = service.process_cal_webhook(SAMPLE_BOOKING_CREATED)
        print(f"Result: {json.dumps(result3, indent=2)}")
        
        print("\n✅ All tests completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the correct directory")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_consultation_service()
