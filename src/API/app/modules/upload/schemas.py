"""Upload module schemas."""

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class FileUploadRequest(BaseModel):
    """Schema for file upload request data."""
    
    engagement_name: str = Field(..., max_length=255, description="Engagement name")
    date1: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date 1 (YYYY-MM-DD)")
    date2: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date 2 (YYYY-MM-DD)")
    date3: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date 3 (YYYY-MM-DD)")
    date4: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date 4 (YYYY-MM-DD)")
    
    @validator('engagement_name')
    def validate_engagement_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Engagement name cannot be empty')
        return v.strip()
    
    @validator('date1', 'date2', 'date3', 'date4')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Invalid date format. Use YYYY-MM-DD')


class FileUploadData(BaseModel):
    """Schema for file upload response data."""
    
    file_id: int
    filename: str
    original_filename: str
    engagement_name: str
    upload_date: str
    processed_flag: bool
    line_count: Optional[int] = None
    storage_location: str
    input_location: str
    processing_time_seconds: Optional[float] = None
    file_size_mb: float
    dates: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Schema for file upload API response."""
    
    status: str = "success"
    data: FileUploadData
    message: str = "File uploaded and processed successfully"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FileListItem(BaseModel):
    """Schema for file list item."""
    
    file_id: int
    filename: str
    original_filename: str
    engagement_name: str
    upload_date: str
    processed_flag: bool
    file_size_mb: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Schema for file list API response."""
    
    status: str = "success"
    data: List[FileListItem]
    message: str = "Files retrieved successfully"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FileStatusResponse(BaseModel):
    """Schema for file status API response."""
    
    status: str = "success"
    data: FileUploadData
    message: str = "File status retrieved successfully"
    timestamp: datetime = Field(default_factory=datetime.utcnow)