"""Custom exception classes for the application."""

from typing import Optional, List, Any


class GeoPulseException(Exception):
    """Base exception for GeoPulse application."""
    
    def __init__(self, message: str, error_code: str = "E000"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class ValidationException(GeoPulseException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[str] = None):
        super().__init__(message, "E007")
        self.field = field
        self.value = value


class DuplicateEmailException(GeoPulseException):
    """Raised when email already exists."""
    
    def __init__(self, email: str):
        super().__init__(f"Email already exists: {email}", "E007")
        self.email = email


class DatabaseException(GeoPulseException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "E003")


class FileSystemException(GeoPulseException):
    """Raised when file system operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "E006")


class RateLimitException(GeoPulseException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "E008")


class FileUploadException(GeoPulseException):
    """Raised when file upload operations fail."""
    
    def __init__(self, message: str, filename: Optional[str] = None, user_id: Optional[int] = None):
        super().__init__(message, "E001")
        self.filename = filename
        self.user_id = user_id


class FileProcessingException(GeoPulseException):
    """Raised when file processing operations fail."""
    
    def __init__(self, message: str, file_id: Optional[int] = None, operation: Optional[str] = None):
        super().__init__(message, "E005")
        self.file_id = file_id
        self.operation = operation


class StorageException(GeoPulseException):
    """Raised when storage operations fail."""
    
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__(message, "E006")
        self.path = path


class AuthenticationException(GeoPulseException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "E004")