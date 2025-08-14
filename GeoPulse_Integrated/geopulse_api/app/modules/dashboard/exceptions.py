"""Custom exceptions for dashboard module."""

from typing import Optional


class DashboardException(Exception):
    """Base exception for dashboard operations."""
    
    def __init__(self, message: str, error_code: str = "E003"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class DashboardAccessException(DashboardException):
    """Raised when user cannot access dashboard data."""
    
    def __init__(self, message: str, user_id: Optional[int] = None):
        super().__init__(message, "E004")
        self.user_id = user_id


class MetricsCalculationException(DashboardException):
    """Raised when metrics calculation fails."""
    
    def __init__(self, message: str, user_id: Optional[int] = None):
        super().__init__(message, "E003")
        self.user_id = user_id


class PaginationException(DashboardException):
    """Raised when pagination parameters are invalid."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, "E007")
        self.field = field