#!/usr/bin/env python3
"""
Simple test script to debug Google Calendar integration
"""
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime

# Load environment variables
load_dotenv()

def test_calendar_direct():
    """Test calendar integration directly"""
    print("🚀 Direct Google Calendar Test")
    print("=" * 40)
    
    try:
        # Get credentials from environment
        private_key = os.getenv('GOOGLE_PRIVATE_KEY')
        client_email = os.getenv('GOOGLE_CLIENT_EMAIL')
        project_id = os.getenv('GOOGLE_PROJECT_ID')
        
        if not private_key or not client_email:
            print("❌ Missing credentials")
            return False
            
        # Handle escaped newlines in private key
        private_key = private_key.replace('\\n', '\n')
        
        info = {
            "type": "service_account",
            "project_id": project_id or "project",
            "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
            "private_key": private_key,
            "client_email": client_email,
            "client_id": os.getenv('GOOGLE_CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL')
        }
        
        creds = service_account.Credentials.from_service_account_info(info, scopes=[
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/calendar.events.readonly'
        ])
        
        delegated_user = os.getenv('GOOGLE_CALENDAR_ID')
        if delegated_user:
            creds = creds.with_subject(delegated_user)
            
        service = build('calendar', 'v3', credentials=creds)
        print("✅ Calendar service created successfully!")
        
        # Test creating an event
        start = datetime.datetime.now() + datetime.timedelta(hours=1)
        end = start + datetime.timedelta(minutes=30)
        
        event = {
            'summary': 'Test Appointment - Debug',
            'description': 'This is a test appointment for debugging',
            'start': {'dateTime': start.isoformat(), 'timeZone': 'America/New_York'},
            'end': {'dateTime': end.isoformat(), 'timeZone': 'America/New_York'},
            'attendees': [{'email': 'scott@uxly.software'}]
        }
        
        result = service.events().insert(calendarId='primary', body=event).execute()
        print(f"✅ Event created successfully!")
        print(f"   Event ID: {result.get('id')}")
        print(f"   Event Link: {result.get('htmlLink')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_calendar_direct()

