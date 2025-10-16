#!/usr/bin/env python3
"""
Seed script for testing consultant dashboard.
Wipes existing data and creates test patients with medical data and consultations.
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import text

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.db import SessionLocal
from app.database.entities import User, PatientProfile, MedicalBackground, Consultation
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.patient_profile_repository import PatientProfileRepository
from app.database.repositories.medical_background_repository import MedicalBackgroundRepository
from app.database.repositories.consultation_repository import ConsultationRepository


def wipe_database(db):
    """Wipe all test data from database."""
    print("🗑️  Wiping existing data...")
    
    # Delete in reverse order of dependencies
    db.execute(text('DELETE FROM consultations'))
    db.execute(text('DELETE FROM medical_backgrounds'))
    db.execute(text('DELETE FROM patient_profiles'))
    db.execute(text('DELETE FROM users'))
    db.commit()
    
    print("✅ Database wiped successfully")


def create_test_users(db):
    """Create test users."""
    print("👥 Creating test users...")
    
    user_repo = UserRepository(db)
    
    users = [
        {
            "phone_number": "john.smith@email.com",
            "name": "John Smith"
        },
        {
            "phone_number": "sarah.j@email.com", 
            "name": "Sarah Johnson"
        },
        {
            "phone_number": "michael.brown@email.com",
            "name": "Michael Brown"
        },
        {
            "phone_number": "emma.wilson@email.com",
            "name": "Emma Wilson"
        }
    ]
    
    created_users = []
    for user_data in users:
        user = user_repo.create(**user_data)
        created_users.append(user)
        print(f"  ✅ Created user: {user.name} ({user.phone_number})")
    
    return created_users


def create_test_patients(db, users):
    """Create test patient profiles."""
    print("🏥 Creating test patient profiles...")
    
    patient_repo = PatientProfileRepository(db)
    
    patients = [
        {
            "user_id": users[0].id,
            "name": "John Smith",
            "phone": "+1-555-0101",
            "email": "john.smith@email.com",
            "age": 30,
            "location": "New York, NY"
        },
        {
            "user_id": users[1].id,
            "name": "Sarah Johnson", 
            "phone": "+1-555-0102",
            "email": "sarah.j@email.com",
            "age": 40,
            "location": "Los Angeles, CA"
        },
        {
            "user_id": users[2].id,
            "name": "Michael Brown",
            "phone": "+1-555-0103", 
            "email": "michael.brown@email.com",
            "age": 50,
            "location": "Chicago, IL"
        },
        {
            "user_id": users[3].id,
            "name": "Emma Wilson",
            "phone": "+1-555-0104",
            "email": "emma.wilson@email.com",
            "age": 35,
            "location": "Miami, FL"
        }
    ]
    
    created_patients = []
    for patient_data in patients:
        patient = patient_repo.create(**patient_data)
        created_patients.append(patient)
        print(f"  ✅ Created patient: {patient.name} ({patient.email})")
    
    return created_patients


def create_test_medical_backgrounds(db, patients):
    """Create test medical background data."""
    print("🩺 Creating test medical backgrounds...")
    
    medical_repo = MedicalBackgroundRepository(db)
    
    medical_data = [
        {
            "patient_profile_id": patients[0].id,
            "medical_data": {
                "age_range": "26-35",
                "current_medications": "yes",
                "current_medications_details": "Multivitamin, Fish oil",
                "allergies": "none",
                "medical_conditions": "none",
                "previous_surgeries": "none",
                "hair_loss_duration": "2-3 years",
                "hair_loss_pattern": ["crown", "temples"],
                "family_history": ["father"],
                "previous_treatments": ["minoxidil"],
                "submitted_at": datetime.now().isoformat()
            }
        },
        {
            "patient_profile_id": patients[1].id,
            "medical_data": {
                "age_range": "36-45",
                "current_medications": "yes",
                "current_medications_details": "Blood pressure medication",
                "allergies": "yes",
                "allergies_details": "Penicillin",
                "medical_conditions": "hypertension",
                "previous_surgeries": "none",
                "hair_loss_duration": "5+ years",
                "hair_loss_pattern": ["front", "crown"],
                "family_history": ["mother", "father"],
                "previous_treatments": ["minoxidil", "finasteride"],
                "submitted_at": datetime.now().isoformat()
            }
        },
        {
            "patient_profile_id": patients[2].id,
            "medical_data": {
                "age_range": "46-55",
                "current_medications": "none",
                "allergies": "none",
                "medical_conditions": "none",
                "previous_surgeries": "none",
                "hair_loss_duration": "3-4 years",
                "hair_loss_pattern": ["crown"],
                "family_history": ["father"],
                "previous_treatments": [],
                "submitted_at": datetime.now().isoformat()
            }
        },
        {
            "patient_profile_id": patients[3].id,
            "medical_data": {
                "age_range": "26-35",
                "current_medications": "yes",
                "current_medications_details": "Birth control, Iron supplement",
                "allergies": "none",
                "medical_conditions": "none",
                "previous_surgeries": "appendectomy",
                "previous_surgeries_details": "2018",
                "hair_loss_duration": "1-2 years",
                "hair_loss_pattern": ["front", "temples"],
                "family_history": ["mother"],
                "previous_treatments": ["biotin"],
                "submitted_at": datetime.now().isoformat()
            }
        }
    ]
    
    for data in medical_data:
        medical = medical_repo.create(**data)
        print(f"  ✅ Created medical background for patient {data['patient_profile_id']}")


def create_test_consultations(db, patients):
    """Create test consultations."""
    print("📅 Creating test consultations...")
    
    consultation_repo = ConsultationRepository(db)
    
    # Today's consultations
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    consultations = [
        {
            "zoom_meeting_id": "123456789",
            "topic": "Hair Transplant Consultation - John Smith",
            "attendee_name": "John Smith",
            "attendee_email": "john.smith@email.com",
            "host_name": "Dr. Istanbul Medic",
            "host_email": "doctor@istanbulmedic.com",
            "raw_payload": {"type": "test_consultation", "patient_id": str(patients[0].id)},
            "patient_profile_id": patients[0].id,
            "status": "scheduled",
            "agenda": "Initial consultation for hair transplant procedure",
            "start_time": today.replace(hour=10, minute=0),
            "duration": 30,
            "timezone": "America/New_York"
        },
        {
            "zoom_meeting_id": "123456790",
            "topic": "Follow-up Consultation - Sarah Johnson",
            "attendee_name": "Sarah Johnson",
            "attendee_email": "sarah.j@email.com",
            "host_name": "Dr. Istanbul Medic",
            "host_email": "doctor@istanbulmedic.com",
            "raw_payload": {"type": "test_consultation", "patient_id": str(patients[1].id)},
            "patient_profile_id": patients[1].id,
            "status": "scheduled",
            "agenda": "Follow-up consultation for hair transplant",
            "start_time": today.replace(hour=14, minute=30),
            "duration": 30,
            "timezone": "America/Los_Angeles"
        },
        # Tomorrow's consultation
        {
            "zoom_meeting_id": "123456791",
            "topic": "Initial Consultation - Michael Brown",
            "attendee_name": "Michael Brown",
            "attendee_email": "michael.brown@email.com",
            "host_name": "Dr. Istanbul Medic",
            "host_email": "doctor@istanbulmedic.com",
            "raw_payload": {"type": "test_consultation", "patient_id": str(patients[2].id)},
            "patient_profile_id": patients[2].id,
            "status": "scheduled",
            "agenda": "First consultation for hair loss treatment",
            "start_time": (today + timedelta(days=1)).replace(hour=9, minute=0),
            "duration": 30,
            "timezone": "America/Chicago"
        },
        # Past consultation
        {
            "zoom_meeting_id": "123456792",
            "topic": "Completed Consultation - Emma Wilson",
            "attendee_name": "Emma Wilson",
            "attendee_email": "emma.wilson@email.com",
            "host_name": "Dr. Istanbul Medic",
            "host_email": "doctor@istanbulmedic.com",
            "raw_payload": {"type": "test_consultation", "patient_id": str(patients[3].id)},
            "patient_profile_id": patients[3].id,
            "status": "completed",
            "agenda": "Completed consultation",
            "start_time": (today - timedelta(days=1)).replace(hour=11, minute=0),
            "duration": 30,
            "timezone": "America/New_York"
        }
    ]
    
    for consultation_data in consultations:
        consultation = consultation_repo.create(**consultation_data)
        print(f"  ✅ Created consultation: {consultation.topic} for {consultation.attendee_name}")


def main():
    """Main seeding function."""
    print("🌱 Starting database seeding for consultant dashboard testing...")
    
    db = SessionLocal()
    try:
        # Wipe existing data
        wipe_database(db)
        
        # Create test data
        users = create_test_users(db)
        patients = create_test_patients(db, users)
        create_test_medical_backgrounds(db, patients)
        create_test_consultations(db, patients)
        
        # Verify data
        print("\n📊 Final database state:")
        print(f"  Users: {db.query(User).count()}")
        print(f"  Patient Profiles: {db.query(PatientProfile).count()}")
        print(f"  Medical Backgrounds: {db.query(MedicalBackground).count()}")
        print(f"  Consultations: {db.query(Consultation).count()}")
        
        print("\n✅ Database seeding completed successfully!")
        print("\n🧪 Test data includes:")
        print("  - 4 test patients with medical backgrounds")
        print("  - 2 consultations scheduled for today")
        print("  - 1 consultation scheduled for tomorrow")
        print("  - 1 completed consultation from yesterday")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
