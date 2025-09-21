#!/usr/bin/env python3
"""
Test script to debug Google Calendar integration
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.tools.google_calendar_tools import get_calendar_service, create_calendar_event

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test if all required environment variables are loaded"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'GOOGLE_PRIVATE_KEY',
        'GOOGLE_CLIENT_EMAIL', 
        'GOOGLE_PROJECT_ID',
        'GOOGLE_CALENDAR_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 20}...{value[-4:] if len(value) > 4 else '***'}")
        else:
            print(f"❌ {var}: NOT FOUND")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n🚨 Missing variables: {missing_vars}")
        return False
    else:
        print("\n✅ All required environment variables found!")
        return True

def test_calendar_service():
    """Test if we can create a calendar service"""
    print("\n🔍 Testing Google Calendar service...")
    
    try:
        service = get_calendar_service()
        print("✅ Calendar service created successfully!")
        return service
    except Exception as e:
        print(f"❌ Failed to create calendar service: {e}")
        return None

def test_calendar_event_creation(service):
    """Test creating a calendar event"""
    print("\n🔍 Testing calendar event creation...")
    
    try:
        # Test event creation by calling the function directly
        from app.tools.google_calendar_tools import create_calendar_event
        result = create_calendar_event.func(
            summary="Test Appointment - Debug",
            start_datetime="2024-12-20T15:00:00",
            duration_minutes=30,
            description="This is a test appointment for debugging",
            attendee_email="scott@uxly.software"
        )
        print(f"✅ Event creation result: {result}")
        return True
    except Exception as e:
        print(f"❌ Failed to create calendar event: {e}")
        return False

def main():
    print("🚀 Google Calendar Integration Debug Test")
    print("=" * 50)
    
    # Step 1: Check environment variables
    if not test_environment_variables():
        print("\n❌ Environment variables not properly loaded. Check your .env file.")
        return
    
    # Step 2: Test calendar service
    service = test_calendar_service()
    if not service:
        print("\n❌ Cannot create calendar service. Check your credentials.")
        return
    
    # Step 3: Test event creation
    if test_calendar_event_creation(service):
        print("\n🎉 Google Calendar integration is working!")
    else:
        print("\n❌ Calendar event creation failed. Check permissions and credentials.")

if __name__ == "__main__":
    main()

