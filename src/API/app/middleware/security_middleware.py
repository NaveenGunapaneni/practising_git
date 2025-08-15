"""Security middleware for API protection."""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import get_logger

logger = get_logger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers and protections."""
    
    def __init__(self, app, enable_security_headers: bool = True):
        super().__init__(app)
        self.enable_security_headers = enable_security_headers
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers and protections."""
        
        # Process request
        response = await call_next(request)
        
        if self.enable_security_headers:
            self._add_security_headers(response)
        
        # Log security events if needed
        self._log_security_events(request, response)
        
        return response
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response."""
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (basic)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Strict Transport Security (HTTPS only)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        
        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "speaker=()"
        )
        
        # Remove server information
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Add custom security header
        response.headers["X-API-Version"] = "1.0"
        response.headers["X-Security-Policy"] = "GeoPulse-API-Security-v1"
    
    def _log_security_events(self, request: Request, response: Response):
        """Log security-related events."""
        
        # Log suspicious requests
        suspicious_patterns = [
            "../", "..\\", "<script", "javascript:", "vbscript:",
            "onload=", "onerror=", "eval(", "document.cookie",
            "union select", "drop table", "insert into"
        ]
        
        request_url = str(request.url).lower()
        user_agent = request.headers.get("user-agent", "").lower()
        
        for pattern in suspicious_patterns:
            if pattern in request_url or pattern in user_agent:
                logger.warning("Suspicious request detected", extra={
                    "client_ip": request.client.host if request.client else "unknown",
                    "method": request.method,
                    "url": str(request.url),
                    "user_agent": request.headers.get("user-agent", ""),
                    "pattern": pattern,
                    "security_event": "suspicious_request"
                })
                break
        
        # Log failed authentication attempts
        if response.status_code == 401:
            logger.warning("Authentication failed", extra={
                "client_ip": request.client.host if request.client else "unknown",
                "method": request.method,
                "endpoint": request.url.path,
                "user_agent": request.headers.get("user-agent", ""),
                "security_event": "auth_failure"
            })
        
        # Log potential brute force attempts
        if response.status_code == 429:
            logger.warning("Rate limit exceeded", extra={
                "client_ip": request.client.host if request.client else "unknown",
                "method": request.method,
                "endpoint": request.url.path,
                "security_event": "rate_limit_exceeded"
            })
        
        # Log file upload attempts to non-upload endpoints
        if (request.method == "POST" and 
            "multipart/form-data" in request.headers.get("content-type", "") and
            "/files/upload" not in request.url.path):
            logger.warning("File upload to non-upload endpoint", extra={
                "client_ip": request.client.host if request.client else "unknown",
                "method": request.method,
                "endpoint": request.url.path,
                "security_event": "suspicious_upload"
            })