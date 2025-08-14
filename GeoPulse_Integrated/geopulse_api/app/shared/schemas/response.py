"""Shared response schemas for standardized API responses."""

from datetime import datetime
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field


class StandardResponse(BaseModel):
    """Standard success response format."""
    
    status: str = Field(default="success", description="Response status")
    data: Optional[Any] = Field(None, description="Response data")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    status: str = Field(default="error", description="Error status")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class HealthResponse(BaseModel):
    """Health check response format."""
    
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Health check timestamp")
    checks: Optional[Dict[str, Any]] = Field(None, description="Detailed health checks")