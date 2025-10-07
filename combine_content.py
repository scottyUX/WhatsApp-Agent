#!/usr/bin/env python3
"""
Combine Istanbul Medic and Lenus Clinic content into a single knowledge base file
"""

def combine_content():
    """Combine both content files into a comprehensive knowledge base"""
    
    # Read Istanbul Medic content
    with open('istanbul_medic_content.txt', 'r', encoding='utf-8') as f:
        istanbul_content = f.read()
    
    # Read Lenus Clinic content
    with open('lenus_clinic_content.txt', 'r', encoding='utf-8') as f:
        lenus_content = f.read()
    
    # Create combined content
    combined_content = f"""COMPREHENSIVE HAIR TRANSPLANT KNOWLEDGE BASE
============================================
Combined content from Istanbul Medic and Lenus Clinic
Created: 2025-10-06
Purpose: Vector store content for AI agent

This file contains comprehensive information about hair transplant services
from two leading clinics in Turkey: Istanbul Medic and Lenus Clinic.

============================================
ISTANBUL MEDIC CONTENT
============================================

{istanbul_content}

============================================
LENUS CLINIC CONTENT
============================================

{lenus_content}

============================================
END OF KNOWLEDGE BASE
============================================
"""
    
    # Write combined content
    with open('combined_hair_transplant_knowledge.txt', 'w', encoding='utf-8') as f:
        f.write(combined_content)
    
    print("✅ Combined knowledge base created successfully!")
    print("📄 File: combined_hair_transplant_knowledge.txt")
    
    # Show file sizes
    import os
    istanbul_size = os.path.getsize('istanbul_medic_content.txt')
    lenus_size = os.path.getsize('lenus_clinic_content.txt')
    combined_size = os.path.getsize('combined_hair_transplant_knowledge.txt')
    
    print(f"📊 Istanbul Medic: {istanbul_size:,} bytes")
    print(f"📊 Lenus Clinic: {lenus_size:,} bytes")
    print(f"📊 Combined: {combined_size:,} bytes")

if __name__ == "__main__":
    combine_content()
