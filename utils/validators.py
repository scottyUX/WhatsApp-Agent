"""
Simple validation utilities for testing purposes.
"""

import re
import html
from typing import Optional, Tuple, Dict, Any
import phonenumbers
from phonenumbers import PhoneNumberType


class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def normalize_phone(raw: str, default_region: str | None = None):
    """Simple, robust phone number normalization using libphonenumber"""
    raw = (raw or "").strip()
    errors = []
    parsed = None

    # Try with default region (e.g., "US", "TR", "DE")
    if default_region:
        try:
            parsed = phonenumbers.parse(raw, default_region)
        except phonenumbers.NumberParseException as e:
            errors.append(f"parse_with_region:{e}")

    # Fallback: try as international
    if not parsed:
        try:
            parsed = phonenumbers.parse(raw, None)
        except phonenumbers.NumberParseException as e:
            errors.append(f"parse_international:{e}")
            return {"valid": False, "reason": "unparseable", "errors": errors}

    is_possible = phonenumbers.is_possible_number(parsed)
    is_valid = phonenumbers.is_valid_number(parsed)
    e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164) if is_valid else None
    region = phonenumbers.region_code_for_number(parsed)
    number_type = phonenumbers.number_type(parsed)

    return {
        "valid": bool(is_valid),
        "possible": bool(is_possible),
        "e164": e164,
        "region": region,
        "type": number_type,
        "raw": raw,
        "errors": errors
    }


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email address format"""
    if not email:
        return False, "Email is required"
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False, "Please enter a valid email address"
    
    return True, None


def validate_phone(phone: str, default_region: str = "US", require_mobile: bool = True) -> Tuple[bool, str, str]:
    """Validate phone number using libphonenumber for production-ready validation"""
    if not phone:
        return False, "Phone number is required", ""
    
    result = normalize_phone(phone, default_region)
    
    if not result["valid"]:
        return False, "Please enter a valid phone number with country code (e.g., +1 415 555 2671)", ""
    
    # Check if mobile number is required
    if require_mobile and result["type"] not in [PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE]:
        return False, "This looks like a landline number. For SMS reminders, please provide a mobile number.", ""
    
    return True, "", result["e164"]


def validate_name(name: str) -> Tuple[bool, str]:
    """Validate name format"""
    if not name:
        return False, "Name is required"
    
    # Basic validation - at least 2 characters, no special characters except spaces, hyphens, apostrophes
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long"
    
    if not re.match(r'^[a-zA-Z\s\-\'\.]+$', name.strip()):
        return False, "Name contains invalid characters"
    
    return True, None


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and other attacks"""
    if not text:
        return ""
    
    # HTML escape
    text = html.escape(text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()