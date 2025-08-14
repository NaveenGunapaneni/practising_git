"""Shared validation utilities."""

import re
from datetime import datetime
from typing import List, Optional
from email_validator import validate_email, EmailNotValidError


def validate_email_format(email: str) -> bool:
    """Validate email format."""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def validate_phone_format(phone: str) -> bool:
    """Validate phone number format."""
    # Basic phone validation - can be enhanced based on requirements
    phone_pattern = r'^\+?[\d\s\-\(\)]{10,20}$'
    return bool(re.match(phone_pattern, phone.strip()))


def validate_date_format(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """Validate date format."""
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def validate_password_strength(password: str) -> tuple[bool, List[str]]:
    """Validate password strength and return issues."""
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")
    
    return len(issues) == 0, issues


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input."""
    if not value:
        return ""
    
    # Strip whitespace
    value = value.strip()
    
    # Remove null bytes and control characters
    value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
    
    # Limit length if specified
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension."""
    if not filename:
        return False
    
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return f'.{file_ext}' in [ext.lower() for ext in allowed_extensions]