"""Error handling system for converting exceptions to HTTP responses."""

from datetime import datetime
from typing import List, Dict, Any
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    GeoPulseException,
    ValidationException,
    DuplicateEmailException,
    DatabaseException,
    FileSystemException,
    RateLimitException
)


class ErrorHandler:
    """Handler for converting exceptions to structured HTTP responses."""
    
    @staticmethod
    def handle_validation_exception(exc: ValidationException) -> JSONResponse:
        """Handle validation exceptions."""
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
                "details": {
                    "field": exc.field,
                    "value": exc.value
                } if exc.field else None,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def handle_duplicate_email_exception(exc: DuplicateEmailException) -> JSONResponse:
        """Handle duplicate email exceptions."""
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
                "details": {
                    "field": "email",
                    "constraint": "unique"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def handle_database_exception(exc: DatabaseException) -> JSONResponse:
        """Handle database exceptions."""
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": "Database operation failed",
                "details": {
                    "internal_message": exc.message
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def handle_filesystem_exception(exc: FileSystemException) -> JSONResponse:
        """Handle file system exceptions."""
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": "File system operation failed",
                "details": {
                    "internal_message": exc.message
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def handle_rate_limit_exception(exc: RateLimitException) -> JSONResponse:
        """Handle rate limit exceptions."""
        return JSONResponse(
            status_code=429,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
                "details": {
                    "retry_after": "60 seconds"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def handle_generic_exception(exc: Exception) -> JSONResponse:
        """Handle generic exceptions."""
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_code": "E000",
                "message": "Internal server error",
                "details": {
                    "internal_message": str(exc)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def handle_exception(exc: Exception) -> JSONResponse:
        """
        Main exception handler that routes to specific handlers.
        
        Args:
            exc: Exception to handle
            
        Returns:
            JSONResponse with appropriate error format
        """
        if isinstance(exc, ValidationException):
            return ErrorHandler.handle_validation_exception(exc)
        elif isinstance(exc, DuplicateEmailException):
            return ErrorHandler.handle_duplicate_email_exception(exc)
        elif isinstance(exc, DatabaseException):
            return ErrorHandler.handle_database_exception(exc)
        elif isinstance(exc, FileSystemException):
            return ErrorHandler.handle_filesystem_exception(exc)
        elif isinstance(exc, RateLimitException):
            return ErrorHandler.handle_rate_limit_exception(exc)
        else:
            return ErrorHandler.handle_generic_exception(exc)
    
    @staticmethod
    def create_validation_error_response(errors: List[ValidationException]) -> Dict[str, Any]:
        """
        Create validation error response for multiple errors.
        
        Args:
            errors: List of validation exceptions
            
        Returns:
            Dictionary containing error response
        """
        error_details = []
        for error in errors:
            error_details.append({
                "field": error.field,
                "message": error.message,
                "value": error.value
            })
        
        return {
            "status": "error",
            "error_code": "E007",
            "message": "Validation failed",
            "details": error_details,
            "timestamp": datetime.utcnow().isoformat()
        }