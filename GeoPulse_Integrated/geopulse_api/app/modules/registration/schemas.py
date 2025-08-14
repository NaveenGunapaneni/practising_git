"""Registration module schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from email_validator import validate_email, EmailNotValidError

from app.shared.utils.validation import validate_phone_format, sanitize_string


class UserRegistrationRequest(BaseModel):
    """Schema for user registration request."""
    
    organization_name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    user_name: str = Field(..., min_length=1, max_length=255, description="User full name")
    contact_phone: str = Field(..., min_length=10, max_length=20, description="Contact phone number")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")
    
    @validator('organization_name', 'user_name')
    def sanitize_text_fields(cls, v):
        return sanitize_string(v, max_length=255)
    
    @validator('email')
    def validate_email_format(cls, v):
        try:
            validate_email(v)
            return v.lower().strip()
        except EmailNotValidError:
            raise ValueError('Invalid email format')
    
    @validator('contact_phone')
    def validate_phone(cls, v):
        if not validate_phone_format(v):
            raise ValueError('Invalid phone number format')
        return v.strip()
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserData(BaseModel):
    """Schema for user data in responses."""
    
    user_id: int
    organization_name: str
    user_name: str
    contact_phone: str
    email: str
    logo_path: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserRegistrationResponse(BaseModel):
    """Schema for user registration response."""
    
    status: str = "success"
    data: UserData
    message: str = "User registered successfully"
    timestamp: datetime = Field(default_factory=datetime.utcnow)