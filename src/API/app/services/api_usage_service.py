"""
API Usage Service for managing Sentinel Hub API call limits and tracking
"""

from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user_api_usage import UserAPIUsage
from app.shared.models.base import User
from app.core.logger import get_logger

logger = get_logger(__name__)


class APIUsageService:
    """Service for managing user API usage and limits."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_api_usage_for_user(self, user_id: int, allowed_calls: int = 50) -> UserAPIUsage:
        """Create API usage record for a new user."""
        try:
            api_usage = UserAPIUsage.create_for_user(user_id, allowed_calls)
            self.db.add(api_usage)
            await self.db.commit()
            await self.db.refresh(api_usage)
            
            logger.info(f"Created API usage record for user {user_id} with {allowed_calls} allowed calls")
            return api_usage
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create API usage for user {user_id}: {str(e)}")
            raise
    
    async def get_user_api_usage(self, user_id: int) -> Optional[UserAPIUsage]:
        """Get API usage record for a user."""
        result = await self.db.execute(
            select(UserAPIUsage).where(UserAPIUsage.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def check_api_limit(self, user_id: int, required_calls: int = 1) -> Tuple[bool, str, Optional[dict]]:
        """
        Check if user can make the required number of API calls.
        
        Args:
            user_id: User ID
            required_calls: Number of API calls needed
            
        Returns:
            Tuple of (can_make_calls, error_message, usage_info)
        """
        try:
            api_usage = await self.get_user_api_usage(user_id)
            
            if not api_usage:
                return False, "API usage record not found. Please contact support.", None
            
            can_make_calls, error_message = api_usage.can_make_api_calls(required_calls)
            usage_info = api_usage.get_usage_summary()
            
            if not can_make_calls:
                logger.warning(f"API limit check failed for user {user_id}: {error_message}")
            
            return can_make_calls, error_message, usage_info
            
        except Exception as e:
            logger.error(f"Error checking API limit for user {user_id}: {str(e)}")
            return False, "Error checking API limits. Please try again.", None
    
    async def increment_api_usage(self, user_id: int, successful_calls: int) -> bool:
        """
        Increment the API usage counter for successful calls.
        
        Args:
            user_id: User ID
            successful_calls: Number of successful API calls to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            api_usage = await self.get_user_api_usage(user_id)
            
            if not api_usage:
                logger.error(f"API usage record not found for user {user_id}")
                return False
            
            old_count = api_usage.performed_api_calls
            api_usage.increment_api_calls(successful_calls)
            await self.db.commit()
            
            logger.info(f"Updated API usage for user {user_id}: {old_count} -> {api_usage.performed_api_calls} (+{successful_calls})")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to increment API usage for user {user_id}: {str(e)}")
            return False
    
    async def get_usage_summary(self, user_id: int) -> Optional[dict]:
        """Get detailed usage summary for a user."""
        api_usage = await self.get_user_api_usage(user_id)
        return api_usage.get_usage_summary() if api_usage else None
    
    def extend_user_expiry(self, user_id: int, days: int = 30) -> bool:
        """Extend user's API access expiry date."""
        try:
            api_usage = self.get_user_api_usage(user_id)
            
            if not api_usage:
                logger.error(f"API usage record not found for user {user_id}")
                return False
            
            old_expiry = api_usage.user_expiry_date
            api_usage.extend_expiry(days)
            self.db.commit()
            
            logger.info(f"Extended expiry for user {user_id}: {old_expiry} -> {api_usage.user_expiry_date}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to extend expiry for user {user_id}: {str(e)}")
            return False
    
    def reset_user_api_calls(self, user_id: int, new_limit: Optional[int] = None) -> bool:
        """Reset user's API call counter and optionally update limit."""
        try:
            api_usage = self.get_user_api_usage(user_id)
            
            if not api_usage:
                logger.error(f"API usage record not found for user {user_id}")
                return False
            
            old_count = api_usage.performed_api_calls
            old_limit = api_usage.allowed_api_calls
            
            api_usage.reset_api_calls(new_limit)
            self.db.commit()
            
            logger.info(f"Reset API calls for user {user_id}: {old_count} -> 0, limit: {old_limit} -> {api_usage.allowed_api_calls}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to reset API calls for user {user_id}: {str(e)}")
            return False
    
    def get_all_users_usage(self) -> list[dict]:
        """Get usage summary for all users (admin function)."""
        try:
            api_usages = self.db.query(UserAPIUsage).all()
            return [usage.get_usage_summary() for usage in api_usages]
            
        except Exception as e:
            logger.error(f"Failed to get all users usage: {str(e)}")
            return []
    
    def cleanup_expired_users(self) -> int:
        """Clean up expired user records (optional maintenance function)."""
        try:
            expired_count = self.db.query(UserAPIUsage).filter(
                UserAPIUsage.user_expiry_date < datetime.utcnow()
            ).count()
            
            logger.info(f"Found {expired_count} expired user API usage records")
            return expired_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired users: {str(e)}")
            return 0