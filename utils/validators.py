import re
import html
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class InputValidator:
    """Comprehensive input validation for WhatsApp Agent"""
    
    # Email validation regex
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # Phone number validation regex (supports various formats)
    PHONE_REGEX = re.compile(
        r'^(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
    )
    
    # International phone regex (more flexible, but requires at least 7 digits)
    INTERNATIONAL_PHONE_REGEX = re.compile(
        r'^\+?[1-9]\d{6,14}$'
    )
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize user input to prevent XSS and other security issues
        
        Args:
            text: Raw user input
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove HTML tags and escape special characters
        sanitized = html.escape(text.strip())
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email address is required"
        
        email = email.strip().lower()
        
        if len(email) > 254:
            return False, "Email address is too long"
        
        if not InputValidator.EMAIL_REGEX.match(email):
            return False, "Please enter a valid email address (e.g., user@example.com)"
        
        # Check for common typos
        common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        domain = email.split('@')[1] if '@' in email else ''
        
        if domain in ['gmial.com', 'gmai.com', 'gmail.co']:
            return False, f"Did you mean 'gmail.com' instead of '{domain}'?"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str, str]:
        """
        Validate phone number format - requires country code for international app
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message, formatted_phone)
        """
        if not phone:
            return False, "Phone number is required", ""
        
        # Clean the phone number
        cleaned = re.sub(r'[^\d+]', '', phone.strip())
        
        # Must start with + for international format
        if not cleaned.startswith('+'):
            return False, "Please include country code (e.g., +1 for US, +44 for UK, +33 for France)", ""
        
        # Check if it's a valid international number
        if InputValidator.INTERNATIONAL_PHONE_REGEX.match(cleaned):
            return True, "", cleaned
        
        # Check if it's a valid US phone number with +1
        if cleaned.startswith('+1') and len(cleaned) == 12:
            return True, "", cleaned
        
        return False, "Please enter a valid international phone number with country code (e.g., +1234567890, +44123456789)", ""
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """
        Validate full name format
        
        Args:
            name: Full name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Full name is required"
        
        name = InputValidator.sanitize_input(name)
        
        if len(name) < 2:
            return False, "Name must be at least 2 characters long"
        
        if len(name) > 100:
            return False, "Name is too long (maximum 100 characters)"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
            return False, "Name can only contain letters, spaces, hyphens, apostrophes, and periods"
        
        # Check for at least one letter
        if not re.search(r'[a-zA-Z]', name):
            return False, "Name must contain at least one letter"
        
        return True, ""
    
    @staticmethod
    def validate_appointment_data(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate complete appointment data
        
        Args:
            data: Dictionary containing appointment data
            
        Returns:
            Tuple of (is_valid, error_message, cleaned_data)
        """
        cleaned_data = {}
        errors = []
        
        # Validate name
        if 'name' in data:
            is_valid, error = InputValidator.validate_name(data['name'])
            if not is_valid:
                errors.append(f"Name: {error}")
            else:
                cleaned_data['name'] = InputValidator.sanitize_input(data['name'])
        
        # Validate email
        if 'email' in data:
            is_valid, error = InputValidator.validate_email(data['email'])
            if not is_valid:
                errors.append(f"Email: {error}")
            else:
                cleaned_data['email'] = data['email'].strip().lower()
        
        # Validate phone
        if 'phone' in data:
            is_valid, error, formatted_phone = InputValidator.validate_phone(data['phone'])
            if not is_valid:
                errors.append(f"Phone: {error}")
            else:
                cleaned_data['phone'] = formatted_phone
        
        # Validate appointment time (if provided)
        if 'appointment_time' in data:
            try:
                # Parse the appointment time
                if isinstance(data['appointment_time'], str):
                    # Try to parse ISO format
                    parsed_time = datetime.fromisoformat(data['appointment_time'].replace('Z', '+00:00'))
                    cleaned_data['appointment_time'] = parsed_time.isoformat()
                else:
                    cleaned_data['appointment_time'] = data['appointment_time']
            except (ValueError, TypeError):
                errors.append("Appointment time: Invalid date format")
        
        if errors:
            return False, "; ".join(errors), {}
        
        return True, "", cleaned_data
    
    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, str]:
        """
        Extract contact information from user input text
        
        Args:
            text: Raw user input that may contain name, phone, email
            
        Returns:
            Dictionary with extracted information
        """
        if not text:
            return {}
        
        text = InputValidator.sanitize_input(text)
        extracted = {}
        
        # Extract email - look for patterns like "email is xyz" or just standalone emails
        email_patterns = [
            r'email\s+is\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Valid email format
            r'email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Valid email format
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Valid email format
            r'email\s+is\s+([a-zA-Z0-9._%+-]+)',  # Any text after "email is" (for validation)
            r'email:\s*([a-zA-Z0-9._%+-]+)',  # Any text after "email:" (for validation)
        ]
        
        for pattern in email_patterns:
            email_match = re.search(pattern, text, re.IGNORECASE)
            if email_match:
                extracted['email'] = email_match.group(1).lower()
                break
        
        # Extract phone number (prioritize international format)
        # Look for phone numbers with country codes first
        phone_patterns = [
            r'phone\s+number\s+is\s+(\+[1-9]\d{6,14})',  # "phone number is +1234567890"
            r'phone\s+is\s+(\+[1-9]\d{6,14})',  # "phone is +1234567890"
            r'phone:\s*(\+[1-9]\d{6,14})',  # "phone: +1234567890"
            r'(\+[1-9]\d{6,14})',  # Just the number with country code
            r'phone\s+number\s+is\s+(\d{10,15})',  # "phone number is 1234567890" (will add +1)
            r'phone\s+is\s+(\d{10,15})',  # "phone is 1234567890" (will add +1)
            r'phone:\s*(\d{10,15})',  # "phone: 1234567890" (will add +1)
            r'phone\s+number\s+is\s+(\d+)',  # "phone number is 12345" (any digits)
            r'phone\s+is\s+(\d+)',  # "phone is 12345" (any digits)
            r'phone:\s*(\d+)',  # "phone: 12345" (any digits)
        ]
        
        phone_found = False
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text, re.IGNORECASE)
            if phone_match:
                phone = phone_match.group(1).replace(' ', '')
                
                # If it doesn't start with +, add +1 for US numbers
                if not phone.startswith('+'):
                    if len(phone) == 10:
                        phone = f"+1{phone}"
                    elif len(phone) == 11 and phone.startswith('1'):
                        phone = f"+{phone}"
                    # For other lengths, keep as is so validation can catch the error
                
                extracted['phone'] = phone
                phone_found = True
                break
        
        # Extract name (everything that's not email or phone)
        name_text = text
        if 'email' in extracted:
            name_text = name_text.replace(extracted['email'], '')
        if 'phone' in extracted:
            name_text = name_text.replace(extracted['phone'], '')
        
        # Clean up name text
        name_text = re.sub(r'\s+', ' ', name_text).strip()
        if name_text and len(name_text) > 1:
            extracted['name'] = name_text
        
        return extracted

# Convenience functions for easy import
def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format"""
    return InputValidator.validate_email(email)

def validate_phone(phone: str) -> Tuple[bool, str, str]:
    """Validate phone number format"""
    return InputValidator.validate_phone(phone)

def validate_name(name: str) -> Tuple[bool, str]:
    """Validate full name format"""
    return InputValidator.validate_name(name)

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    return InputValidator.sanitize_input(text)

def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract contact information from text"""
    return InputValidator.extract_contact_info(text)