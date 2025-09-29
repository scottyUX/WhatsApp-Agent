#!/usr/bin/env python3
"""
Test script for input validation functions
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.validators import validate_email, validate_phone, validate_name, sanitize_input

def test_email_validation():
    """Test email validation"""
    print("🧪 Testing Email Validation")
    print("=" * 40)
    
    test_cases = [
        ("scott@uxly.software", True, "Valid email"),
        ("test@gmail.com", True, "Valid Gmail"),
        ("invalid-email", False, "Invalid format"),
        ("user@domain", False, "Missing TLD"),
        ("", False, "Empty email"),
        ("user@domain.co.uk", True, "Valid UK domain"),
    ]
    
    for email, expected, description in test_cases:
        is_valid, error = validate_email(email)
        status = "✅" if is_valid == expected else "❌"
        print(f"{status} {description}: '{email}' -> {is_valid} ({error if not is_valid else 'OK'})")

def test_phone_validation():
    """Test phone number validation"""
    print("\n🧪 Testing Phone Validation")
    print("=" * 40)
    
    test_cases = [
        ("+18312959447", True, "Valid US number with country code"),
        ("+44 20 7946 0958", False, "UK landline (rejected for SMS)"),
        ("+1234", False, "Invalid short number"),
        ("+123456", False, "Invalid short number"),
        ("8312959447", True, "US number without country code"),
        ("", False, "Empty phone"),
        ("invalid", False, "Invalid format"),
        ("+1 415 555 2671", True, "Valid formatted US number"),
    ]
    
    for phone, expected, description in test_cases:
        is_valid, error, formatted = validate_phone(phone)
        status = "✅" if is_valid == expected else "❌"
        print(f"{status} {description}: '{phone}' -> {is_valid} ({error if not is_valid else formatted})")

def test_name_validation():
    """Test name validation"""
    print("\n🧪 Testing Name Validation")
    print("=" * 40)
    
    test_cases = [
        ("Scott Davis", True, "Valid name"),
        ("John", True, "Single name"),
        ("Mary-Jane", True, "Name with hyphen"),
        ("O'Connor", True, "Name with apostrophe"),
        ("", False, "Empty name"),
        ("A", False, "Too short"),
        ("John123", False, "Contains numbers"),
        ("John@Doe", False, "Contains special chars"),
    ]
    
    for name, expected, description in test_cases:
        is_valid, error = validate_name(name)
        status = "✅" if is_valid == expected else "❌"
        print(f"{status} {description}: '{name}' -> {is_valid} ({error if not is_valid else 'OK'})")

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
        sanitized = sanitize_input(text)
        print(f"🧹 {description}: '{text}' -> '{sanitized}'")

def main():
    """Run all validation tests"""
    print("🚀 Starting Validation Tests")
    print("=" * 50)
    
    test_email_validation()
    test_phone_validation()
    test_name_validation()
    test_sanitization()
    
    print("\n✅ All validation tests completed!")

if __name__ == "__main__":
    main()