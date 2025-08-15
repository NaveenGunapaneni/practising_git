"""Login module schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Schema for login request."""
    
    username: str = Field(..., description="Username (email address)")
    password: str = Field(..., description="Password")


class UserProfile(BaseModel):
    """Schema for user profile in token response."""
    
    user_id: int
    user_name: str
    email: str
    organization_name: str
    logo_path: str
    
    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """Schema for JWT token data."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserProfile


class LoginResponse(BaseModel):
    """Schema for login response."""
    
    status: str = "success"
    data: TokenData
    message: str = "Login successful"
    timestamp: datetime = Field(default_factory=datetime.utcnow)