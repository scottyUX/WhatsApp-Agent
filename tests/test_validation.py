#!/usr/bin/env python3
"""
Test script for input validation functions
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.validators import InputValidator, validate_email, validate_phone, validate_name, extract_contact_info

def test_email_validation():
    """Test email validation"""
    print("🧪 Testing Email Validation")
    print("=" * 40)
    
    test_cases = [
        ("scott@uxly.software", True, "Valid email"),
        ("test@gmail.com", True, "Valid Gmail"),
        ("invalid-email", False, "Invalid format"),
        ("user@domain", False, "Missing TLD"),
        ("@domain.com", False, "Missing username"),
        ("user@", False, "Missing domain"),
        ("", False, "Empty email"),
        ("user@domain.co.uk", True, "Valid UK domain"),
        ("test+tag@gmail.com", True, "Valid with plus"),
        ("user.name@domain.com", True, "Valid with dots"),
    ]
    
    for email, expected, description in test_cases:
        is_valid, error = validate_email(email)
        status = "✅" if is_valid == expected else "❌"
        print(f"{status} {description}: {email} -> {is_valid} ({error if not is_valid else 'OK'})")

def test_phone_validation():
    """Test phone validation"""
    print("\n🧪 Testing Phone Validation")
    print("=" * 40)
    
    test_cases = [
        ("+18312959447", True, "US number with country code"),
        ("+44 20 7946 0958", True, "UK number"),
        ("+33 1 42 86 83 26", True, "French number"),
        ("+49 30 12345678", True, "German number"),
        ("+81 3 1234 5678", True, "Japanese number"),
        ("+86 138 0013 8000", True, "Chinese number"),
        ("8312959447", False, "US number without country code"),
        ("(831) 295-9447", False, "Formatted US without country code"),
        ("831-295-9447", False, "Dashed format without country code"),
        ("123", False, "Too short"),
        ("abc-def-ghij", False, "Non-numeric"),
        ("", False, "Empty phone"),
        ("+123", False, "Too short with country code"),
    ]
    
    for phone, expected, description in test_cases:
        is_valid, error, formatted = validate_phone(phone)
        status = "✅" if is_valid == expected else "❌"
        print(f"{status} {description}: {phone} -> {is_valid} ({formatted if is_valid else error})")

def test_name_validation():
    """Test name validation"""
    print("\n🧪 Testing Name Validation")
    print("=" * 40)
    
    test_cases = [
        ("Scott Davis", True, "Valid name"),
        ("Mary Jane Smith", True, "Three names"),
        ("O'Connor", True, "Apostrophe"),
        ("Jean-Pierre", True, "Hyphen"),
        ("Dr. Smith", True, "With title"),
        ("", False, "Empty name"),
        ("A", False, "Too short"),
        ("Scott123", False, "Contains numbers"),
        ("Scott@Davis", False, "Contains special chars"),
        ("Scott Davis " * 20, False, "Too long"),
    ]
    
    for name, expected, description in test_cases:
        is_valid, error = validate_name(name)
        status = "✅" if is_valid == expected else "❌"
        print(f"{status} {description}: '{name}' -> {is_valid} ({error if not is_valid else 'OK'})")

def test_contact_extraction():
    """Test contact information extraction"""
    print("\n🧪 Testing Contact Extraction")
    print("=" * 40)
    
    test_cases = [
        ("Scott Davis +18312959447 scott@uxly.software", "Complete info with country code"),
        ("My name is John Smith, call me at +1 555 123-4567 or email john@example.com", "Natural language with country code"),
        ("Contact: jane.doe@company.co.uk +44 20 7946 0958", "International"),
        ("Just my email: test@gmail.com", "Email only"),
        ("Call me at +1 555-123-4567", "Phone only with country code"),
        ("I'm Sarah", "Name only"),
        ("Scott Davis 8312959447 scott@uxly.software", "US number without country code (should add +1)"),
        ("", "Empty input"),
    ]
    
    for text, description in test_cases:
        extracted = extract_contact_info(text)
        print(f"📝 {description}: '{text}'")
        print(f"   Extracted: {extracted}")

def test_sanitization():
    """Test input sanitization"""
    print("\n🧪 Testing Input Sanitization")
    print("=" * 40)
    
    test_cases = [
        ("<script>alert('xss')</script>", "XSS attempt"),
        ("  Multiple   spaces  ", "Extra whitespace"),
        ("Normal text", "Normal input"),
        ("Text with 'quotes' and \"double quotes\"", "Quotes"),
        ("", "Empty input"),
        ("<b>Bold</b> text", "HTML tags"),
    ]
    
    for text, description in test_cases:
        sanitized = InputValidator.sanitize_input(text)
        print(f"🧹 {description}: '{text}' -> '{sanitized}'")

def test_complete_validation():
    """Test complete appointment data validation"""
    print("\n🧪 Testing Complete Validation")
    print("=" * 40)
    
    test_data = {
        "name": "Scott Davis",
        "email": "scott@uxly.software",
        "phone": "8312959447",
        "appointment_time": "2024-12-20T15:00:00"
    }
    
    is_valid, error, cleaned = InputValidator.validate_appointment_data(test_data)
    print(f"📋 Complete data validation:")
    print(f"   Valid: {is_valid}")
    print(f"   Error: {error}")
    print(f"   Cleaned: {cleaned}")

def main():
    """Run all validation tests"""
    print("🚀 Input Validation Test Suite")
    print("=" * 50)
    
    test_email_validation()
    test_phone_validation()
    test_name_validation()
    test_contact_extraction()
    test_sanitization()
    test_complete_validation()
    
    print("\n✅ All validation tests completed!")

if __name__ == "__main__":
    main()

