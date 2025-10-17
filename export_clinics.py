#!/usr/bin/env python3
"""
Script to export clinic data from Supabase database and generate JSON file for frontend
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import sys

# Database connection
DATABASE_URL = "postgresql://postgres:UxlySoftware2025!@db.ulwkvusfbvnzdbjczkyi.supabase.co:5432/postgres"

def connect_to_database():
    """Connect to the Supabase database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def export_clinics():
    """Export all clinic data from the database"""
    conn = connect_to_database()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Query to get all clinics from the clinics table
        query = """
        SELECT 
            id,
            title,
            location,
            rating,
            reviews_count,
            categories,
            image_url,
            phone,
            email,
            website,
            opening_hours,
            additional_info,
            price_range,
            availability,
            country,
            city,
            created_at,
            updated_at
        FROM clinics
        ORDER BY rating DESC, reviews_count DESC
        """
        
        print("Fetching clinics from database...")
        cursor.execute(query)
        clinics = cursor.fetchall()
        
        print(f"Found {len(clinics)} clinics in database")
        
        # Convert to list of dictionaries
        clinics_list = []
        for clinic in clinics:
            clinic_dict = {
                "id": clinic['id'],
                "name": clinic['title'] or "Unknown Clinic",
                "rating": float(clinic['rating']) if clinic['rating'] else 0.0,
                "reviews": int(clinic['reviews_count']) if clinic['reviews_count'] else 0,
                "categories": clinic['categories'] if clinic['categories'] else [],
                "address": clinic['location'] or "Address not available",
                "phone": clinic['phone'] or "Phone not available",
                "email": clinic['email'] or "",
                "website": clinic['website'] or "",
                "image": clinic['image_url'] or "/results/clinic_default.jpg",
                "opening_hours": clinic['opening_hours'] if clinic['opening_hours'] else {
                    "monday": "9:00 AM - 6:00 PM",
                    "tuesday": "9:00 AM - 6:00 PM", 
                    "wednesday": "9:00 AM - 6:00 PM",
                    "thursday": "9:00 AM - 6:00 PM",
                    "friday": "9:00 AM - 6:00 PM",
                    "saturday": "9:00 AM - 4:00 PM",
                    "sunday": "Closed"
                },
                "additional_info": clinic['additional_info'] if clinic['additional_info'] else {
                    "languages": ["English"],
                    "payment_methods": ["Cash", "Credit Card"],
                    "accommodation": "Hotel booking assistance available",
                    "airport_transfer": "Airport transfer available"
                },
                "price_range": clinic['price_range'] or "Contact for pricing",
                "availability": clinic['availability'] or "Contact for availability",
                "country": clinic['country'] or "Unknown",
                "city": clinic['city'] or "Unknown"
            }
            clinics_list.append(clinic_dict)
        
        # Create the final JSON structure
        result = {
            "clinics": clinics_list,
            "total": len(clinics_list),
            "total_pages": 1,
            "exported_at": datetime.now().isoformat(),
            "source": "Supabase Database"
        }
        
        return result
        
    except Exception as e:
        print(f"Error exporting clinics: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def save_to_json(data, output_path):
    """Save the data to a JSON file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully exported {data['total']} clinics to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting clinic data export...")
    
    # Export data from database
    data = export_clinics()
    if not data:
        print("❌ Failed to export clinic data")
        sys.exit(1)
    
    # Define output path
    output_path = "/Users/scottdavis/istanbulmedic-website-fe/src/data/clinics.json"
    
    # Save to JSON file
    if save_to_json(data, output_path):
        print(f"📊 Export Summary:")
        print(f"   - Total clinics: {data['total']}")
        print(f"   - Output file: {output_path}")
        print(f"   - Export time: {data['exported_at']}")
        print("✅ Export completed successfully!")
    else:
        print("❌ Failed to save JSON file")
        sys.exit(1)

if __name__ == "__main__":
    main()


