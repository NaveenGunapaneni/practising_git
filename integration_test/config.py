"""Integration Testing Configuration."""

import os
from typing import Dict, Any
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
TEST_DATA_DIR = BASE_DIR / "test_data"
OUTPUT_DIR = BASE_DIR / "test_outputs"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

# Create directories if they don't exist
TEST_DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Application URLs
BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# API Endpoints
API_ENDPOINTS = {
    "health": f"{API_BASE_URL}/api/v1/health",
    "register": f"{API_BASE_URL}/api/v1/auth/register",
    "login": f"{API_BASE_URL}/api/v1/auth/login",
    "dashboard": f"{API_BASE_URL}/api/v1/dashboard",
    "upload": f"{API_BASE_URL}/api/v1/files/upload",
    "list_files": f"{API_BASE_URL}/api/v1/files/list",
    "download": f"{API_BASE_URL}/api/v1/files/{{file_id}}/download",
    "view_file": f"{API_BASE_URL}/api/v1/files/{{file_id}}/view",
}

# UI Pages
UI_PAGES = {
    "login": f"{BASE_URL}/login",
    "register": f"{BASE_URL}/register",
    "dashboard": f"{BASE_URL}/dashboard",
    "upload": f"{BASE_URL}/upload",
}

# Test Configuration
TEST_CONFIG = {
    "timeout": 30,
    "implicit_wait": 10,
    "headless": os.getenv("HEADLESS", "false").lower() == "true",
    "browser": os.getenv("BROWSER", "chrome"),
    "screenshot_on_failure": True,
    "retry_count": 3,
}

# Test Data
TEST_USER = {
    "organization_name": "Test Organization",
    "user_name": "Test User",
    "contact_phone": "1234567890",
    "email": "test@example.com",
    "password": "TestPass123!",
}

# Sample file paths
SAMPLE_FILES = {
    "valid_xlsx": TEST_DATA_DIR / "sample_valid.xlsx",
    "valid_csv": TEST_DATA_DIR / "sample_valid.csv",
    "invalid_format": TEST_DATA_DIR / "sample_invalid.txt",
    "large_file": TEST_DATA_DIR / "sample_large.xlsx",
}

# Expected file formats and validation rules
FILE_VALIDATION = {
    "allowed_extensions": [".xlsx", ".csv", ".xls"],
    "max_file_size_mb": 50,
    "required_columns": ["latitude", "longitude", "date", "value"],
    "output_format": "xlsx",
}

# Database configuration for testing
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5433")),
    "database": os.getenv("DB_NAME", "geopulse_db"),
    "user": os.getenv("DB_USER", "geopulse_user"),
    "password": os.getenv("DB_PASSWORD", "geopulse_secure_123"),
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": BASE_DIR / "test.log",
}

# Test categories
TEST_CATEGORIES = {
    "smoke": "Basic functionality tests",
    "regression": "Comprehensive functionality tests",
    "performance": "Performance and load tests",
    "security": "Security and authentication tests",
}

# Expected response schemas
RESPONSE_SCHEMAS = {
    "success": {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["success"]},
            "data": {"type": "object"},
            "message": {"type": "string"},
            "timestamp": {"type": "string"},
        },
        "required": ["status", "data", "message", "timestamp"],
    },
    "error": {
        "type": "object",
        "properties": {
            "detail": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error_code": {"type": "string"},
                    "message": {"type": "string"},
                    "details": {"type": "array"},
                    "timestamp": {"type": "string"},
                },
            }
        },
        "required": ["detail"],
    },
}
