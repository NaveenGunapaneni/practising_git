"""Logging middleware for request/response tracking."""

import time
import json
from datetime import datetime
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging of requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        start_time = time.time()
        
        # Extract request details
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log request
        logger.info("Request received", extra={
            "method": request.method,
            "endpoint": request.url.path
        })
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log successful response
            logger.info("Request completed", extra={
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": response.status_code
            })
            
            return response
            
        except Exception as e:
            # Calculate duration for failed requests
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log error
            logger.error("Request failed", extra={
                "method": request.method,
                "endpoint": request.url.path,
                "error": f"{type(e).__name__}: {str(e)}"
            })
            
            raise