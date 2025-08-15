"""Registration module services."""

import bcrypt
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from app.modules.registration.repository import RegistrationRepository
from app.modules.registration.schemas import UserRegistrationRequest, UserData
from app.modules.registration.models import User
from app.config import settings
from app.core.exceptions import ValidationException, DuplicateEmailException
from app.core.logger import get_logger

logger = get_logger(__name__)


class RegistrationService:
    """Service for user registration business logic."""
    
    def __init__(self, repository: RegistrationRepository):
        self.repository = repository
        self.user_json_dir = Path(settings.user_json_dir)
    
    async def register_user(self, user_data: UserRegistrationRequest) -> User:
        """
        Register a new user with complete workflow.
        
        Args:
            user_data: User registration request data
            
        Returns:
            Created user instance
            
        Raises:
            ValidationException: If validation fails
            DuplicateEmailException: If email already exists
        """
        logger.info(f"Starting user registration for email: {user_data.email}")
        
        try:
            # Check if email already exists
            if await self.repository.email_exists(user_data.email):
                raise DuplicateEmailException(user_data.email)
            
            # Hash password using bcrypt
            password_hash = self._hash_password(user_data.password)
            
            # Prepare user data for database
            db_user_data = {
                "organization_name": user_data.organization_name,
                "user_name": user_data.user_name,
                "contact_phone": user_data.contact_phone,
                "email": user_data.email,
                "password_hash": password_hash,
                "logo_path": "/defaults/datalegos.png"  # Default logo
            }
            
            # Create user in database
            user = await self.repository.create_user(db_user_data)
            
            # Create user JSON file
            await self._create_user_json_file(user)
            
            logger.info(f"User registration completed successfully: {user.user_id}")
            return user
            
        except (ValidationException, DuplicateEmailException):
            # Re-raise known exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error during user registration: {str(e)}")
            raise ValidationException(f"Registration failed: {str(e)}")
    
    async def _create_user_json_file(self, user: User) -> None:
        """Create JSON file for user data."""
        try:
            user_json_data = {
                "user_id": user.user_id,
                "organization_name": user.organization_name,
                "user_name": user.user_name,
                "contact_phone": user.contact_phone,
                "email": user.email,
                "logo_path": user.logo_path,
                "registration_date": user.created_at.isoformat() if user.created_at else None,
                "file_count": 0
            }
            
            # Generate filename from user name
            safe_name = "".join(c for c in user.user_name.lower() if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"{safe_name}.json"
            
            await self._write_user_json_file(filename, user_json_data)
            
            logger.info(f"User JSON file created: {filename}")
            
        except Exception as e:
            # Log error but don't fail registration for JSON file creation
            logger.warning(f"Failed to create user JSON file: {str(e)}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        if not password or len(password) < 6:
            raise ValidationException("Password must be at least 6 characters long")
        
        salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    async def _write_user_json_file(self, filename: str, user_data: Dict[str, Any]) -> None:
        """Create user JSON file."""
        try:
            # Ensure directory exists
            self.user_json_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = self.user_json_dir / filename
            
            # Write JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise ValidationException(f"Failed to create user JSON file: {str(e)}")
    
    def validate_registration_data(self, user_data: UserRegistrationRequest) -> None:
        """Validate registration data."""
        # Additional business logic validation can be added here
        # Basic validation is handled by Pydantic in the schema
        pass