"""Registration module repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.modules.registration.models import User
from app.core.exceptions import DatabaseException, DuplicateEmailException


class RegistrationRepository:
    """Repository for user registration database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: dict) -> User:
        """Create a new user in the database."""
        try:
            user = User(**user_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
            
        except IntegrityError as e:
            await self.db.rollback()
            if "email" in str(e.orig):
                raise DuplicateEmailException(user_data.get("email", ""))
            raise DatabaseException(f"Failed to create user: {str(e)}")
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Database error during user creation: {str(e)}")
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"Failed to get user by email: {str(e)}")
    
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        user = await self.get_user_by_email(email)
        return user is not None