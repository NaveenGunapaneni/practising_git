"""Dashboard API routes and endpoints."""

from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.logger import get_logger
from app.shared.utils.security import get_current_user
from app.modules.upload.models import User
from .schemas import (
    DashboardResponse, 
    DashboardErrorResponse, 
    DashboardQueryParams
)
from .services import DashboardService
from .repository import DashboardRepository
from .exceptions import DashboardAccessException, MetricsCalculationException, PaginationException

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_dashboard_service(db: AsyncSession = Depends(get_db_session)) -> DashboardService:
    """Dependency injection for dashboard service."""
    repository = DashboardRepository(db)
    return DashboardService(repository)


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Get Dashboard Data",
    description="Retrieve comprehensive dashboard data for authenticated users including file information, user details, and processing metrics.",
    responses={
        200: {"description": "Dashboard data retrieved successfully"},
        401: {"description": "Invalid or expired token", "model": DashboardErrorResponse},
        422: {"description": "Invalid query parameters", "model": DashboardErrorResponse},
        500: {"description": "Internal server error", "model": DashboardErrorResponse}
    }
)
async def get_dashboard_data(
    limit: Annotated[int, Query(ge=1, le=100, description="Number of items per page")] = 50,
    offset: Annotated[int, Query(ge=0, le=10000, description="Number of items to skip")] = 0,
    sort_by: Annotated[str, Query(pattern="^(upload_date|filename|engagement_name)$", description="Field to sort by")] = "upload_date",
    sort_order: Annotated[str, Query(pattern="^(asc|desc)$", description="Sort order")] = "desc",
    status: Annotated[str, Query(pattern="^(all|processed|pending)$", description="Filter by processing status")] = "all",
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
) -> DashboardResponse:
    """
    Get comprehensive dashboard data for the authenticated user.
    
    This endpoint provides:
    - User profile information
    - File upload history with filtering and pagination
    - Processing metrics and statistics
    - Pagination information
    
    Query parameters allow for customization of the data view:
    - **limit**: Number of files to return (1-100, default: 50)
    - **offset**: Number of files to skip for pagination (0-10000, default: 0)
    - **sort_by**: Field to sort files by (upload_date, filename, engagement_name, default: upload_date)
    - **sort_order**: Sort order (asc, desc, default: desc)
    - **status**: Filter files by processing status (all, processed, pending, default: all)
    """
    try:
        # Create query parameters object
        params = DashboardQueryParams(
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
            status=status
        )
        
        # Retrieve dashboard data
        dashboard_data = await dashboard_service.get_dashboard_data(
            user_id=current_user.user_id,
            params=params
        )
        
        # Return successful response
        return DashboardResponse(
            status="success",
            data=dashboard_data,
            message="Dashboard data retrieved successfully",
            timestamp=datetime.utcnow()
        )
        
    except DashboardAccessException as e:
        logger.error(f"Dashboard access denied for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "error_code": e.error_code,
                "message": e.message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except PaginationException as e:
        logger.error(f"Invalid pagination parameters for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail={
                "status": "error",
                "error_code": e.error_code,
                "message": e.message,
                "details": [{"field": e.field, "message": e.message}] if e.field else [],
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except MetricsCalculationException as e:
        logger.error(f"Metrics calculation failed for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": e.error_code,
                "message": "Failed to retrieve dashboard data",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in dashboard endpoint for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "E003",
                "message": "Failed to retrieve dashboard data",
                "timestamp": datetime.utcnow().isoformat()
            }
        )