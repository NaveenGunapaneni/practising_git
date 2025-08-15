"""
API Usage endpoints for checking and managing user API limits
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db_session
from app.services.api_usage_service import APIUsageService
from app.core.auth import get_current_user
from app.shared.models.base import User

router = APIRouter(prefix="/api-usage", tags=["API Usage"])


@router.get("/status", response_model=Dict[str, Any])
async def get_api_usage_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user's API usage status and limits."""
    
    try:
        api_service = APIUsageService(db)
        usage_summary = await api_service.get_usage_summary(current_user.user_id)
        
        if not usage_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API usage record not found. Please contact support."
            )
        
        return {
            "status": "success",
            "data": usage_summary,
            "message": "API usage status retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve API usage status: {str(e)}"
        )


@router.get("/check-limit/{required_calls}")
async def check_api_limit(
    required_calls: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Check if user can make the specified number of API calls."""
    
    if required_calls <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Required calls must be greater than 0"
        )
    
    try:
        api_service = APIUsageService(db)
        can_make_calls, error_message, usage_info = await api_service.check_api_limit(
            current_user.user_id, 
            required_calls
        )
        
        return {
            "status": "success" if can_make_calls else "error",
            "data": {
                "can_make_calls": can_make_calls,
                "required_calls": required_calls,
                "error_message": error_message if not can_make_calls else None,
                "usage_info": usage_info
            },
            "message": "API limit check completed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check API limit: {str(e)}"
        )


@router.post("/extend-expiry/{days}")
async def extend_user_expiry(
    days: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Extend user's API access expiry date (admin function)."""
    
    if days <= 0 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be between 1 and 365"
        )
    
    try:
        api_service = APIUsageService(db)
        success = api_service.extend_user_expiry(current_user.user_id, days)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API usage record not found"
            )
        
        # Get updated usage info
        usage_summary = api_service.get_usage_summary(current_user.user_id)
        
        return {
            "status": "success",
            "data": usage_summary,
            "message": f"API access extended by {days} days"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extend API access: {str(e)}"
        )


@router.post("/reset-calls")
async def reset_api_calls(
    new_limit: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Reset user's API call counter and optionally update limit (admin function)."""
    
    if new_limit is not None and (new_limit <= 0 or new_limit > 10000):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New limit must be between 1 and 10000"
        )
    
    try:
        api_service = APIUsageService(db)
        success = api_service.reset_user_api_calls(current_user.user_id, new_limit)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API usage record not found"
            )
        
        # Get updated usage info
        usage_summary = api_service.get_usage_summary(current_user.user_id)
        
        return {
            "status": "success",
            "data": usage_summary,
            "message": f"API calls reset successfully" + (f" with new limit: {new_limit}" if new_limit else "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset API calls: {str(e)}"
        )