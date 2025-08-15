"""Structured logging configuration."""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
from app.config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for simple structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as simple structured JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        # Add only essential extra fields
        if hasattr(record, 'method') and hasattr(record, 'endpoint'):
            log_data["request"] = f"{record.method} {record.endpoint}"
        
        if hasattr(record, 'status_code'):
            log_data["status"] = record.status_code
        
        if hasattr(record, 'error'):
            log_data["error"] = record.error
        
        # Add exception info if present
        if record.exc_info:
            log_data["error"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Set log level
        logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(StructuredFormatter())
        logger.addHandler(console_handler)
        
        # Create file handler
        log_file_path = settings.log_file
        # Create logs directory if it doesn't exist
        Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)
        
        # Prevent duplicate logs
        logger.propagate = False
    
    return logger


class StructuredLogger:
    """Structured logger for application events."""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def log_registration_attempt(self, email: str, ip: str, user_agent: str):
        """Log user registration attempt."""
        self.logger.info("User registration attempt", extra={
            "event": "registration_attempt",
            "email": email,
            "ip_address": ip,
            "user_agent": user_agent
        })
    
    def log_registration_success(self, user_id: int, email: str, ip: str):
        """Log successful user registration."""
        self.logger.info("User registration successful", extra={
            "event": "registration_success",
            "user_id": user_id,
            "email": email,
            "ip_address": ip
        })
    
    def log_registration_failure(self, email: str, error: str, ip: str):
        """Log failed user registration."""
        self.logger.warning("User registration failed", extra={
            "event": "registration_failure",
            "email": email,
            "error": error,
            "ip_address": ip
        })
    
    def log_database_operation(self, operation: str, table: str, duration_ms: float):
        """Log database operations."""
        self.logger.info("Database operation", extra={
            "event": "database_operation",
            "operation": operation,
            "table": table,
            "duration_ms": duration_ms
        })
    
    def log_file_operation(self, operation: str, file_path: str, success: bool):
        """Log file operations."""
        level = "info" if success else "error"
        getattr(self.logger, level)("File operation", extra={
            "event": "file_operation",
            "operation": operation,
            "file_path": file_path,
            "success": success
        })