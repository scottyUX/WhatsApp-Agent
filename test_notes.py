#!/usr/bin/env python3
"""
Test script for consultant notes functionality.
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
TEST_PATIENT_ID = "test-patient-123"  # You'll need to replace this with a real patient ID

def test_notes_api():
    """Test the consultant notes API endpoints."""
    
    print("🧪 Testing Consultant Notes API...")
    
    # Test 1: Create a note
    print("\n1. Creating a test note...")
    create_data = {
        "patient_profile_id": TEST_PATIENT_ID,
        "note_content": "This is a test note for the consultant notes feature.",
        "note_type": "general",
        "is_private": False
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/consultant-notes/", json=create_data)
        if response.status_code == 200:
            note = response.json()
            print(f"✅ Note created successfully: {note['id']}")
            note_id = note['id']
        else:
            print(f"❌ Failed to create note: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating note: {e}")
        return
    
    # Test 2: Get notes for patient
    print("\n2. Fetching notes for patient...")
    try:
        response = requests.get(f"{API_BASE}/api/consultant-notes/patient/{TEST_PATIENT_ID}")
        if response.status_code == 200:
            notes = response.json()
            print(f"✅ Found {len(notes)} notes for patient")
            for note in notes:
                print(f"   - {note['note_type']}: {note['note_content'][:50]}...")
        else:
            print(f"❌ Failed to fetch notes: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error fetching notes: {e}")
    
    # Test 3: Update the note
    print("\n3. Updating the note...")
    update_data = {
        "note_content": "This is an updated test note with more details.",
        "note_type": "consultation",
        "is_private": True
    }
    
    try:
        response = requests.put(f"{API_BASE}/api/consultant-notes/{note_id}", json=update_data)
        if response.status_code == 200:
            updated_note = response.json()
            print(f"✅ Note updated successfully")
            print(f"   - Type: {updated_note['note_type']}")
            print(f"   - Private: {updated_note['is_private']}")
        else:
            print(f"❌ Failed to update note: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error updating note: {e}")
    
    # Test 4: Delete the note
    print("\n4. Deleting the note...")
    try:
        response = requests.delete(f"{API_BASE}/api/consultant-notes/{note_id}")
        if response.status_code == 200:
            print("✅ Note deleted successfully")
        else:
            print(f"❌ Failed to delete note: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error deleting note: {e}")
    
    # Test 5: Health check
    print("\n5. Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/api/consultant-notes/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health check passed: {health['message']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in health check: {e}")
    
    print("\n🎉 Notes API testing completed!")

if __name__ == "__main__":
    test_notes_api()

