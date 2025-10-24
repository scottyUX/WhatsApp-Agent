#!/usr/bin/env python3
"""
Script to create 4 sample packages and assign them to all clinics.
"""

import uuid
from decimal import Decimal
from app.database.db import engine, SessionLocal
from app.database.repositories.package_repository import PackageRepository
from app.database.repositories.clinic_repository import ClinicRepository
from sqlalchemy import text

def delete_existing_packages():
    """Delete all existing packages."""
    print("🗑️ Deleting all existing packages...")
    
    with engine.connect() as conn:
        result = conn.execute(text('DELETE FROM packages'))
        deleted_count = result.rowcount
        conn.commit()
        print(f"✅ Deleted {deleted_count} existing packages")
        
        # Clear package_ids from all clinics
        conn.execute(text("UPDATE clinics SET package_ids = '{}'::uuid[]"))
        conn.commit()
        print("✅ Cleared package_ids from all clinics")

def create_sample_packages():
    """Create the 4 sample packages."""
    print("\n📦 Creating 4 sample packages...")
    
    packages_data = [
        {
            "name": "Basic Program",
            "description": "Essential hair transplant package with quality care and standard amenities",
            "price": Decimal("2500.00"),
            "currency": "EUR",
            "is_active": True,
            "grafts_count": "2000",
            "hair_transplantation_method": "FUE Transplant Method",
            "stem_cell_therapy_sessions": 0,
            "airport_lounge_access_included": False,
            "airport_lounge_access_details": None,
            "breakfast_included": False,
            "hotel_name": "Basic Hotel",
            "hotel_nights_included": 2,
            "hotel_star_rating": 3,
            "private_translator_included": False,
            "vip_transfer_details": "Hotel only",
            "aftercare_kit_supply_duration": "3 months",
            "laser_sessions": 0,
            "online_follow_ups_duration": "6 months",
            "oxygen_therapy_sessions": 0,
            "post_operation_medication_included": True,
            "prp_sessions_included": False,
            "sedation_included": True
        },
        {
            "name": "Standard Program",
            "description": "High quality hair transplant with advanced DHI method and comprehensive aftercare",
            "price": Decimal("3800.00"),
            "currency": "EUR",
            "is_active": True,
            "grafts_count": "3000",
            "hair_transplantation_method": "DHI Transplant Method",
            "stem_cell_therapy_sessions": 0,
            "airport_lounge_access_included": False,
            "airport_lounge_access_details": None,
            "breakfast_included": False,
            "hotel_name": "Standard Hotel",
            "hotel_nights_included": 3,
            "hotel_star_rating": 4,
            "private_translator_included": False,
            "vip_transfer_details": "Airport - hotel - clinic",
            "aftercare_kit_supply_duration": "6 months",
            "laser_sessions": 1,
            "online_follow_ups_duration": "Lifetime",
            "oxygen_therapy_sessions": 0,
            "post_operation_medication_included": True,
            "prp_sessions_included": False,
            "sedation_included": True
        },
        {
            "name": "Premium Program",
            "description": "Enhanced hair transplant experience with premium amenities, luxury accommodation, and extended care services",
            "price": Decimal("5500.00"),
            "currency": "EUR",
            "is_active": True,
            "grafts_count": "4000",
            "hair_transplantation_method": "DHI Transplant Method",
            "stem_cell_therapy_sessions": 1,
            "airport_lounge_access_included": True,
            "airport_lounge_access_details": "IST only",
            "breakfast_included": True,
            "hotel_name": "Premium Hotel",
            "hotel_nights_included": 4,
            "hotel_star_rating": 5,
            "private_translator_included": True,
            "vip_transfer_details": "Airport - hotel - clinic",
            "aftercare_kit_supply_duration": "6 months",
            "laser_sessions": 2,
            "online_follow_ups_duration": "12 months",
            "oxygen_therapy_sessions": 1,
            "post_operation_medication_included": True,
            "prp_sessions_included": True,
            "sedation_included": True
        },
        {
            "name": "Advanced Treatment Program",
            "description": "VIP concierge service hair transplant with unlimited grafts, luxury accommodation, and lifetime post-operative care",
            "price": Decimal("8200.00"),
            "currency": "EUR",
            "is_active": True,
            "grafts_count": "Unlimited",
            "hair_transplantation_method": "DHI Transplant Method",
            "stem_cell_therapy_sessions": 1,
            "airport_lounge_access_included": True,
            "airport_lounge_access_details": "IST only",
            "breakfast_included": True,
            "hotel_name": "Marriot Sisli Hotel",
            "hotel_nights_included": 3,
            "hotel_star_rating": 5,
            "private_translator_included": True,
            "vip_transfer_details": "Airport - hotel - clinic",
            "aftercare_kit_supply_duration": "3 months",
            "laser_sessions": 1,
            "online_follow_ups_duration": "Lifetime",
            "oxygen_therapy_sessions": 1,
            "post_operation_medication_included": True,
            "prp_sessions_included": True,
            "sedation_included": True
        }
    ]
    
    db = SessionLocal()
    try:
        repo = PackageRepository(db)
        created_packages = []
        
        for package_data in packages_data:
            package = repo.create(**package_data)
            created_packages.append(package)
            print(f"✅ Created: {package.name} - €{package.price}")
        
        return created_packages
    finally:
        db.close()

def assign_packages_to_all_clinics(packages):
    """Assign all packages to every clinic."""
    print(f"\n🏥 Assigning {len(packages)} packages to all clinics...")
    
    db = SessionLocal()
    try:
        clinic_repo = ClinicRepository(db)
        from app.database.entities.clinic import Clinic
        
        # Get all clinics
        all_clinics = db.query(Clinic).all()
        
        for clinic in all_clinics:
            clinic_repo.set_packages(clinic, packages)
            print(f"✅ Assigned packages to: {clinic.title}")
        
        print(f"\n🎉 Successfully assigned packages to {len(all_clinics)} clinics!")
        
    finally:
        db.close()

def main():
    """Main execution function."""
    print("🚀 Starting package creation and assignment process...")
    
    try:
        # Step 1: Delete existing packages
        delete_existing_packages()
        
        # Step 2: Create new packages
        packages = create_sample_packages()
        
        # Step 3: Assign to all clinics
        assign_packages_to_all_clinics(packages)
        
        print("\n✅ Process completed successfully!")
        print("📦 4 packages created and assigned to all clinics")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
