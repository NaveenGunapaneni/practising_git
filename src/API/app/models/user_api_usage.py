"""
User API Usage Model for Sentinel Hub API call tracking and limiting
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Column, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserAPIUsage(Base):
    """Model for tracking user API usage and limits."""
    
    __tablename__ = "user_api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    allowed_api_calls = Column(Integer, default=50, nullable=False)
    performed_api_calls = Column(Integer, default=0, nullable=False)
    user_created_date = Column(TIMESTAMP(timezone=True), nullable=False)
    user_expiry_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="api_usage")
    
    @classmethod
    def create_for_user(cls, user_id: int, allowed_calls: int = 50) -> 'UserAPIUsage':
        """Create API usage record for a new user."""
        created_date = datetime.utcnow()
        expiry_date = created_date + timedelta(days=30)  # 1 month from creation
        
        return cls(
            user_id=user_id,
            allowed_api_calls=allowed_calls,
            performed_api_calls=0,
            user_created_date=created_date,
            user_expiry_date=expiry_date
        )
    
    def can_make_api_calls(self, required_calls: int = 1) -> tuple[bool, str]:
        """
        Check if user can make the required number of API calls.
        
        Args:
            required_calls: Number of API calls needed
            
        Returns:
            Tuple of (can_make_calls, error_message)
        """
        # Check if user account has expired
        # Use timezone-aware datetime for comparison
        current_time = datetime.utcnow().replace(tzinfo=self.user_expiry_date.tzinfo)
        if current_time > self.user_expiry_date:
            return False, f"User account expired on {self.user_expiry_date.strftime('%Y-%m-%d')}. Please renew your subscription."
        
        # Check if user has enough API calls remaining
        remaining_calls = self.allowed_api_calls - self.performed_api_calls
        if remaining_calls < required_calls:
            return False, f"API call limit exceeded. Used: {self.performed_api_calls}/{self.allowed_api_calls}. Need {required_calls} more calls."
        
        return True, ""
    
    def increment_api_calls(self, successful_calls: int):
        """Increment the performed API calls counter."""
        self.performed_api_calls += successful_calls
        self.updated_at = datetime.utcnow()
    
    def get_usage_summary(self) -> dict:
        """Get usage summary for the user."""
        remaining_calls = max(0, self.allowed_api_calls - self.performed_api_calls)
        # Use timezone-aware datetime for comparison
        current_time = datetime.utcnow().replace(tzinfo=self.user_expiry_date.tzinfo)
        days_until_expiry = (self.user_expiry_date - current_time).days
        
        return {
            "user_id": self.user_id,
            "allowed_calls": self.allowed_api_calls,
            "performed_calls": self.performed_api_calls,
            "remaining_calls": remaining_calls,
            "usage_percentage": round((self.performed_api_calls / self.allowed_api_calls) * 100, 2),
            "account_created": self.user_created_date.strftime('%Y-%m-%d'),
            "account_expires": self.user_expiry_date.strftime('%Y-%m-%d'),
            "days_until_expiry": max(0, days_until_expiry),
            "is_expired": current_time > self.user_expiry_date
        }
    
    def extend_expiry(self, days: int = 30):
        """Extend user expiry date."""
        # Use timezone-aware datetime for comparison
        current_time = datetime.utcnow().replace(tzinfo=self.user_expiry_date.tzinfo)
        if current_time > self.user_expiry_date:
            # If already expired, extend from today
            self.user_expiry_date = current_time + timedelta(days=days)
        else:
            # If not expired, extend from current expiry date
            self.user_expiry_date += timedelta(days=days)
        self.updated_at = datetime.utcnow()
    
    def reset_api_calls(self, new_limit: Optional[int] = None):
        """Reset API call counter and optionally update limit."""
        self.performed_api_calls = 0
        if new_limit is not None:
            self.allowed_api_calls = new_limit
        self.updated_at = datetime.utcnow()