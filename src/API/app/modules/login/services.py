"""Login module services."""

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional, Dict, Any
from fastapi import Request

from app.modules.login.repository import LoginRepository
from app.modules.login.schemas import LoginRequest, LoginResponse, TokenData, UserProfile
from app.modules.login.models import User
from app.config import settings
from app.core.exceptions import ValidationException, AuthenticationException
from app.core.logger import get_logger

logger = get_logger(__name__)


class LoginService:
    """Service for user authentication and login."""
    
    def __init__(self, repository: LoginRepository):
        self.repository = repository
    
    async def authenticate_user(
        self, 
        credentials: LoginRequest, 
        client_ip: str, 
        user_agent: str
    ) -> LoginResponse:
        """
        Authenticate user credentials and return JWT token.
        
        Args:
            credentials: User login credentials
            client_ip: Client IP address
            user_agent: Client user agent
            
        Returns:
            Login response with JWT token and user data
            
        Raises:
            AuthenticationException: If authentication fails
            ValidationException: If input validation fails
        """
        email = credentials.username
        password = credentials.password
        
        # Log authentication attempt
        logger.info("User login attempt", extra={
            "email": email,
            "ip_address": client_ip
        })
        
        try:
            # Look up user by email
            user = await self.repository.get_user_by_email(email)
            
            if user is None:
                # User doesn't exist - return generic error to prevent user enumeration
                logger.warning("Login attempt for non-existent user", extra={
                    "email": email,
                    "ip_address": client_ip
                })
                raise AuthenticationException("Invalid credentials")
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                # Password is incorrect
                logger.warning("Failed login attempt - invalid password", extra={
                    "user_id": user.user_id,
                    "email": email,
                    "ip_address": client_ip
                })
                raise AuthenticationException("Invalid credentials")
            
            # Authentication successful
            return await self._handle_successful_login(user, client_ip, user_agent)
            
        except AuthenticationException:
            # Re-raise authentication exceptions
            raise
        except Exception as e:
            logger.error("Unexpected error during authentication", extra={
                "email": email,
                "ip_address": client_ip,
                "error": str(e)
            })
            raise ValidationException(f"Authentication failed: {str(e)}")
    
    async def _handle_successful_login(self, user: User, client_ip: str, user_agent: str) -> LoginResponse:
        """
        Handle successful user authentication.
        
        Args:
            user: Authenticated user
            client_ip: Client IP address
            user_agent: Client user agent
            
        Returns:
            Login response with JWT token
        """
        try:
            # Generate JWT token
            token_data = self._generate_token(user)
            
            # Create response
            response = LoginResponse(
                data=token_data,
                timestamp=datetime.utcnow()
            )
            
            # Log successful authentication
            logger.info("User login successful", extra={
                "user_id": user.user_id,
                "email": user.email,
                "ip_address": client_ip
            })
            
            return response
            
        except Exception as e:
            logger.error("Failed to complete successful login", extra={
                "user_id": user.user_id,
                "email": user.email,
                "error": str(e)
            })
            raise ValidationException(f"Login completion failed: {str(e)}")
    
    def get_client_info(self, request: Request) -> Tuple[str, str]:
        """
        Extract client IP and user agent from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Tuple of (client_ip, user_agent)
        """
        # Get client IP (handle proxy headers)
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.headers.get("X-Real-IP", "")
        if not client_ip and request.client:
            client_ip = request.client.host
        
        # Get user agent
        user_agent = request.headers.get("User-Agent", "")
        
        return client_ip or "unknown", user_agent or "unknown"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash using bcrypt."""
        if not password or not password_hash:
            return False
        
        try:
            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False
    
    def _generate_token(self, user: User) -> TokenData:
        """Generate JWT access token for authenticated user."""
        try:
            # Calculate expiration time
            now = datetime.now(timezone.utc)
            expiration = now + timedelta(minutes=settings.jwt_expiration_minutes)
            
            # Create token payload
            payload = {
                "sub": user.user_id,
                "email": user.email,
                "role": "user",
                "iat": int(now.timestamp()),
                "exp": int(expiration.timestamp())
            }
            
            # Generate token
            access_token = jwt.encode(
                payload, 
                settings.jwt_secret_key, 
                algorithm=settings.jwt_algorithm
            )
            
            # Prepare user profile
            user_profile = UserProfile(
                user_id=user.user_id,
                user_name=user.user_name,
                email=user.email,
                organization_name=user.organization_name,
                logo_path=user.logo_path
            )
            
            return TokenData(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.jwt_expiration_minutes * 60,
                user=user_profile
            )
            
        except Exception as e:
            raise ValidationException(f"Failed to generate JWT token: {str(e)}")