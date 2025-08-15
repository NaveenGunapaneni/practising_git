#!/usr/bin/env python3
"""
Setup script for API Usage Control System
- Runs database migration
- Creates API usage records for existing users
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session, engine
from app.shared.models.base import User
from app.models.user_api_usage import UserAPIUsage
from app.core.logger import get_logger
from sqlalchemy import select

logger = get_logger(__name__)


async def create_api_usage_for_existing_users():
    """Create API usage records for all existing users who don't have them."""
    
    try:
        async with AsyncSession(engine) as db:
            # Get all users
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            logger.info(f"Found {len(users)} existing users")
            
            created_count = 0
            
            for user in users:
                # Check if user already has API usage record
                existing_usage = await db.execute(
                    select(UserAPIUsage).where(UserAPIUsage.user_id == user.user_id)
                )
                
                if existing_usage.scalar_one_or_none() is None:
                    # Create API usage record for this user
                    api_usage = UserAPIUsage.create_for_user(
                        user_id=user.user_id,
                        allowed_calls=50  # Default limit
                    )
                    
                    db.add(api_usage)
                    created_count += 1
                    
                    logger.info(f"Created API usage record for user {user.user_id} ({user.email})")
                else:
                    logger.info(f"API usage record already exists for user {user.user_id} ({user.email})")
            
            # Commit all changes
            await db.commit()
            
            logger.info(f"✅ API usage setup completed!")
            logger.info(f"   Created records for {created_count} users")
            logger.info(f"   Total users with API usage records: {len(users)}")
            
            return created_count
            
    except Exception as e:
        logger.error(f"Failed to create API usage records: {str(e)}")
        raise


async def verify_api_usage_setup():
    """Verify that API usage records are properly set up."""
    
    try:
        async with AsyncSession(engine) as db:
            # Count users and API usage records
            users_result = await db.execute(select(User))
            users_count = len(users_result.scalars().all())
            
            usage_result = await db.execute(select(UserAPIUsage))
            usage_count = len(usage_result.scalars().all())
            
            logger.info(f"📊 VERIFICATION RESULTS:")
            logger.info(f"   Total users: {users_count}")
            logger.info(f"   Total API usage records: {usage_count}")
            
            if users_count == usage_count:
                logger.info(f"✅ All users have API usage records!")
            else:
                logger.warning(f"⚠️ Mismatch: {users_count - usage_count} users missing API usage records")
            
            # Show sample API usage records
            sample_usage = await db.execute(
                select(UserAPIUsage, User)
                .join(User, UserAPIUsage.user_id == User.user_id)
                .limit(3)
            )
            
            logger.info(f"📋 SAMPLE API USAGE RECORDS:")
            for usage, user in sample_usage:
                logger.info(f"   User: {user.email}")
                logger.info(f"     Allowed calls: {usage.allowed_api_calls}")
                logger.info(f"     Performed calls: {usage.performed_api_calls}")
                logger.info(f"     Expires: {usage.user_expiry_date.strftime('%Y-%m-%d')}")
                logger.info(f"     Days remaining: {(usage.user_expiry_date - datetime.utcnow()).days}")
            
    except Exception as e:
        logger.error(f"Failed to verify API usage setup: {str(e)}")
        raise


async def main():
    """Main setup function."""
    
    logger.info("🚀 Starting API Usage Control System Setup")
    
    try:
        # Step 1: Create API usage records for existing users
        logger.info("📝 Creating API usage records for existing users...")
        created_count = await create_api_usage_for_existing_users()
        
        # Step 2: Verify setup
        logger.info("🔍 Verifying API usage setup...")
        await verify_api_usage_setup()
        
        logger.info("🎉 API Usage Control System setup completed successfully!")
        
        if created_count > 0:
            logger.info(f"💡 Next steps:")
            logger.info(f"   - All existing users now have 50 API calls allowed")
            logger.info(f"   - Accounts expire 30 days from today")
            logger.info(f"   - New users will automatically get API usage records during registration")
            logger.info(f"   - Use the /api/v1/api-usage endpoints to manage user limits")
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())