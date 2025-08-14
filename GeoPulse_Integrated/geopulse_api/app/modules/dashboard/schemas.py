"""Dashboard module schemas and data models."""

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field


class DashboardQueryParams(BaseModel):
    """Query parameters for dashboard API requests."""
    
    limit: int = Field(50, ge=1, le=100, description="Number of items per page")
    offset: int = Field(0, ge=0, le=10000, description="Number of items to skip")
    sort_by: str = Field(
        "upload_date", 
        pattern="^(upload_date|filename|engagement_name)$",
        description="Field to sort by"
    )
    sort_order: str = Field(
        "desc", 
        pattern="^(asc|desc)$",
        description="Sort order"
    )
    status: str = Field(
        "all", 
        pattern="^(all|processed|pending)$",
        description="Filter by processing status"
    )


class UserDashboardInfo(BaseModel):
    """User information for dashboard display."""
    
    user_id: int
    user_name: str
    email: str
    organization_name: Optional[str] = None
    logo_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FileDashboardInfo(BaseModel):
    """File information for dashboard display."""
    
    file_id: int
    filename: str
    original_filename: str
    upload_date: date
    engagement_name: str
    processed_flag: bool
    line_count: Optional[int] = None
    storage_location: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserMetrics(BaseModel):
    """User metrics and statistics for dashboard."""
    
    total_files: int = 0
    processed_files: int = 0
    pending_files: int = 0
    total_lines: int = 0
    average_lines_per_file: float = 0.0
    files_this_month: int = 0
    files_this_week: int = 0
    storage_used_mb: float = 0.0


class PaginationInfo(BaseModel):
    """Pagination information for dashboard responses."""
    
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    has_next: bool
    has_previous: bool


class DashboardData(BaseModel):
    """Complete dashboard data structure."""
    
    user: UserDashboardInfo
    files: List[FileDashboardInfo]
    metrics: UserMetrics
    pagination: PaginationInfo


class DashboardResponse(BaseModel):
    """Standard dashboard API response format."""
    
    status: str = "success"
    data: DashboardData
    message: str
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class DashboardErrorResponse(BaseModel):
    """Error response format for dashboard API."""
    
    status: str = "error"
    error_code: str
    message: str
    details: Optional[List[dict]] = None
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }