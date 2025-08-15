"""Shared security utilities."""

import re
from typing import Optional
from pathlib import Path
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# For now, we'll create a simple mock authentication
# In a real application, this would validate JWT tokens
security = HTTPBearer()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent security issues."""
    if not filename:
        return "unnamed_file"
    
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\.\.+', '.', filename)  # Remove multiple dots
    filename = filename.strip('. ')  # Remove leading/trailing dots and spaces
    
    # Limit length
    if len(filename) > 255:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = name[:255-len(ext)] + ext
    
    return filename or "unnamed_file"


def validate_file_path(file_path: str, base_path: str) -> bool:
    """Validate that file path is within base path (prevent directory traversal)."""
    try:
        base = Path(base_path).resolve()
        target = Path(file_path).resolve()
        
        # Check if target is within base directory
        return str(target).startswith(str(base))
    except (OSError, ValueError):
        return False


def extract_client_ip(headers: dict, client_host: Optional[str] = None) -> Optional[str]:
    """Extract client IP from request headers."""
    # Check proxy headers first
    forwarded_for = headers.get("x-forwarded-for", "")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    real_ip = headers.get("x-real-ip", "")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct client host
    return client_host


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data for logging."""
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ""
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate JWT token and return the authenticated user.
    """
    import jwt
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.shared.models.base import User
    from app.core.database import AsyncSessionLocal
    from app.config import settings
    from sqlalchemy import select
    
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "error_code": "E004",
                "message": "Invalid or expired token"
            }
        )
    
    token = credentials.credentials
    
    try:
        # Decode and validate JWT token
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        
        # Extract user_id from token
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=401,
                detail={
                    "status": "error",
                    "error_code": "E004",
                    "message": "Invalid token payload"
                }
            )
        
        # Convert string user_id back to integer
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=401,
                detail={
                    "status": "error",
                    "error_code": "E004",
                    "message": "Invalid user ID in token"
                }
            )
        
        # Query database for user
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user is None:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "status": "error",
                        "error_code": "E004",
                        "message": "User not found"
                    }
                )
            
            return user
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "error_code": "E004",
                "message": "Token has expired"
            }
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "error_code": "E004",
                "message": "Invalid token"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "error_code": "E004",
                "message": "Authentication failed"
            }
        )