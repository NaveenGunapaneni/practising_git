"""Rate limiting middleware for API protection."""

import time
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque

from app.core.logger import get_logger

logger = get_logger(__name__)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_limit: int = 10
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
        
        # In-memory storage for request tracking
        # In production, use Redis or similar distributed cache
        self.minute_requests: Dict[str, deque] = defaultdict(deque)
        self.hour_requests: Dict[str, deque] = defaultdict(deque)
        self.burst_requests: Dict[str, deque] = defaultdict(deque)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Check rate limits and process request."""
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Skip rate limiting for docs and openapi, but allow health checks to be rate limited
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/middleware-info"]:
            return await call_next(request)
        
        current_time = time.time()
        
        # Check rate limits
        if self._is_rate_limited(client_id, current_time):
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error_code": "E008",
                    "message": "Rate limit exceeded",
                    "details": {
                        "requests_per_minute": self.requests_per_minute,
                        "requests_per_hour": self.requests_per_hour,
                        "retry_after": 60
                    }
                },
                headers={"Retry-After": "60"}
            )
        
        # Record the request
        self._record_request(client_id, current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        self._add_rate_limit_headers(response, client_id, current_time)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get authenticated user ID from JWT token
        try:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                # In a real implementation, decode JWT to get user_id
                # For now, use the token as identifier
                return f"user:{auth_header[7:20]}"  # First 13 chars of token
        except:
            pass
        
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Check for proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP", "")
        if real_ip:
            client_ip = real_ip
        
        return f"ip:{client_ip}"
    
    def _is_rate_limited(self, client_id: str, current_time: float) -> bool:
        """Check if client has exceeded rate limits."""
        
        # Clean old requests
        self._clean_old_requests(client_id, current_time)
        
        # Check burst limit (last 10 seconds)
        burst_count = len(self.burst_requests[client_id])
        if burst_count >= self.burst_limit:
            return True
        
        # Check minute limit
        minute_count = len(self.minute_requests[client_id])
        if minute_count >= self.requests_per_minute:
            return True
        
        # Check hour limit
        hour_count = len(self.hour_requests[client_id])
        if hour_count >= self.requests_per_hour:
            return True
        
        return False
    
    def _record_request(self, client_id: str, current_time: float):
        """Record a request for rate limiting."""
        self.burst_requests[client_id].append(current_time)
        self.minute_requests[client_id].append(current_time)
        self.hour_requests[client_id].append(current_time)
    
    def _clean_old_requests(self, client_id: str, current_time: float):
        """Remove old requests from tracking."""
        
        # Clean burst requests (older than 10 seconds)
        burst_cutoff = current_time - 10
        while (self.burst_requests[client_id] and 
               self.burst_requests[client_id][0] < burst_cutoff):
            self.burst_requests[client_id].popleft()
        
        # Clean minute requests (older than 60 seconds)
        minute_cutoff = current_time - 60
        while (self.minute_requests[client_id] and 
               self.minute_requests[client_id][0] < minute_cutoff):
            self.minute_requests[client_id].popleft()
        
        # Clean hour requests (older than 3600 seconds)
        hour_cutoff = current_time - 3600
        while (self.hour_requests[client_id] and 
               self.hour_requests[client_id][0] < hour_cutoff):
            self.hour_requests[client_id].popleft()
    
    def _add_rate_limit_headers(self, response: Response, client_id: str, current_time: float):
        """Add rate limiting headers to response."""
        
        # Calculate remaining requests
        minute_remaining = max(0, self.requests_per_minute - len(self.minute_requests[client_id]))
        hour_remaining = max(0, self.requests_per_hour - len(self.hour_requests[client_id]))
        
        # Add headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(minute_remaining)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(hour_remaining)
        
        # Calculate reset times
        minute_reset = int(current_time) + (60 - int(current_time) % 60)
        hour_reset = int(current_time) + (3600 - int(current_time) % 3600)
        
        response.headers["X-RateLimit-Reset-Minute"] = str(minute_reset)
        response.headers["X-RateLimit-Reset-Hour"] = str(hour_reset)