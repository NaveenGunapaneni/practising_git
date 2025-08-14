"""Shared middleware configuration and utilities."""

from typing import List, Type
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limiting_middleware import RateLimitingMiddleware
from app.middleware.security_middleware import SecurityMiddleware
from app.core.logger import get_logger

logger = get_logger(__name__)


class MiddlewareConfig:
    """Configuration for middleware setup."""
    
    def __init__(self):
        # CORS settings
        self.cors_allow_origins = ["*"]  # Configure for production
        self.cors_allow_credentials = True
        self.cors_allow_methods = ["*"]
        self.cors_allow_headers = ["*"]
        
        # Rate limiting settings
        self.rate_limit_enabled = True
        self.requests_per_minute = 60
        self.requests_per_hour = 1000
        self.burst_limit = 10
        
        # Security settings
        self.security_headers_enabled = True
        
        # Logging settings
        self.request_logging_enabled = True
    
    @classmethod
    def from_env(cls) -> "MiddlewareConfig":
        """Load middleware configuration from environment variables."""
        import os
        
        config = cls()
        
        # CORS configuration
        origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
        config.cors_allow_origins = origins.split(",") if origins != "*" else ["*"]
        config.cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        
        # Rate limiting configuration
        config.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        config.requests_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
        config.requests_per_hour = int(os.getenv("RATE_LIMIT_PER_HOUR", 1000))
        config.burst_limit = int(os.getenv("RATE_LIMIT_BURST", 10))
        
        # Security configuration
        config.security_headers_enabled = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
        
        # Logging configuration
        config.request_logging_enabled = os.getenv("REQUEST_LOGGING_ENABLED", "true").lower() == "true"
        
        return config


def configure_middleware(app: FastAPI, config: MiddlewareConfig = None) -> None:
    """Configure all middleware for the FastAPI application."""
    
    if config is None:
        config = MiddlewareConfig.from_env()
    
    logger.info("Configuring middleware...")
    
    # Add middleware in reverse order (last added = first executed)
    
    # 1. Request logging middleware (innermost - logs actual request/response)
    if config.request_logging_enabled:
        app.add_middleware(LoggingMiddleware)
        logger.info("✅ Logging middleware enabled")
    
    # 2. Security middleware (adds security headers)
    if config.security_headers_enabled:
        app.add_middleware(SecurityMiddleware, enable_security_headers=True)
        logger.info("✅ Security middleware enabled")
    
    # 3. Rate limiting middleware (prevents abuse)
    if config.rate_limit_enabled:
        app.add_middleware(
            RateLimitingMiddleware,
            requests_per_minute=config.requests_per_minute,
            requests_per_hour=config.requests_per_hour,
            burst_limit=config.burst_limit
        )
        logger.info(f"✅ Rate limiting middleware enabled ({config.requests_per_minute}/min, {config.requests_per_hour}/hour)")
    
    # 4. CORS middleware (outermost - handles cross-origin requests)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_allow_origins,
        allow_credentials=config.cors_allow_credentials,
        allow_methods=config.cors_allow_methods,
        allow_headers=config.cors_allow_headers,
    )
    logger.info(f"✅ CORS middleware enabled (origins: {config.cors_allow_origins})")
    
    logger.info("🎉 All middleware configured successfully")


def get_middleware_info() -> dict:
    """Get information about configured middleware."""
    config = MiddlewareConfig.from_env()
    
    return {
        "middleware": {
            "cors": {
                "enabled": True,
                "allow_origins": config.cors_allow_origins,
                "allow_credentials": config.cors_allow_credentials
            },
            "rate_limiting": {
                "enabled": config.rate_limit_enabled,
                "requests_per_minute": config.requests_per_minute,
                "requests_per_hour": config.requests_per_hour,
                "burst_limit": config.burst_limit
            },
            "security": {
                "enabled": config.security_headers_enabled,
                "headers": [
                    "X-Frame-Options",
                    "X-Content-Type-Options", 
                    "X-XSS-Protection",
                    "Content-Security-Policy",
                    "Strict-Transport-Security"
                ]
            },
            "logging": {
                "enabled": config.request_logging_enabled,
                "structured": True,
                "includes": ["request", "response", "timing", "errors"]
            }
        }
    }