"""Dashboard service for data orchestration and business logic."""

from typing import Optional
from datetime import datetime

from app.core.logger import get_logger
from app.core.exceptions import DatabaseException
from .schemas import DashboardData, DashboardQueryParams, UserDashboardInfo, UserMetrics, PaginationInfo, FileDashboardInfo
from .repository import DashboardRepository
from .exceptions import DashboardAccessException, MetricsCalculationException

logger = get_logger(__name__)


class DashboardService:
    """Service for orchestrating dashboard data retrieval and business logic."""
    
    def __init__(self, repository: DashboardRepository):
        self.repository = repository
    
    async def get_dashboard_data(
        self, 
        user_id: int, 
        params: DashboardQueryParams
    ) -> DashboardData:
        """
        Retrieve comprehensive dashboard data for authenticated user.
        
        Args:
            user_id: ID of the authenticated user
            params: Query parameters for filtering, sorting, and pagination
            
        Returns:
            Complete dashboard data structure
            
        Raises:
            DashboardAccessException: If user cannot access dashboard
            MetricsCalculationException: If metrics calculation fails
            DatabaseException: If database operations fail
        """
        logger.info(f"Dashboard data request started for user {user_id}")
        
        try:
            # Step 1: Retrieve user information
            user_info = await self._get_user_info(user_id)
            
            # Step 2: Retrieve file data with filtering and pagination
            files_data, total_count = await self._get_files_data(user_id, params)
            
            # Step 3: Calculate user metrics
            metrics = await self._calculate_metrics(user_id)
            
            # Step 4: Calculate pagination information
            pagination = self._calculate_pagination(params, total_count)
            
            # Step 5: Assemble complete dashboard data
            dashboard_data = DashboardData(
                user=user_info,
                files=files_data,
                metrics=metrics,
                pagination=pagination
            )
            
            logger.info(f"Dashboard data retrieved successfully for user {user_id}, files: {len(files_data)}, total: {total_count}")
            
            return dashboard_data
            
        except DashboardAccessException:
            logger.error(f"Dashboard access denied for user {user_id}")
            raise
        except MetricsCalculationException:
            logger.error(f"Metrics calculation failed for user {user_id}")
            raise
        except DatabaseException as e:
            logger.error(f"Database error in dashboard service for user {user_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in dashboard service for user {user_id}: {str(e)}")
            raise DatabaseException(f"Failed to retrieve dashboard data: {str(e)}")
    
    async def _get_user_info(self, user_id: int) -> UserDashboardInfo:
        """Retrieve user information for dashboard display."""
        try:
            user_data = await self.repository.get_user_dashboard_info(user_id)
            
            if not user_data:
                raise DashboardAccessException(
                    "User not found or access denied", 
                    user_id=user_id
                )
            
            return UserDashboardInfo.from_orm(user_data)
            
        except Exception as e:
            if isinstance(e, DashboardAccessException):
                raise
            raise DatabaseException(f"Failed to retrieve user information: {str(e)}")
    
    async def _get_files_data(self, user_id: int, params: DashboardQueryParams):
        """Retrieve file data with filtering, sorting, and pagination."""
        try:
            files, total_count = await self.repository.get_user_files_paginated(
                user_id=user_id,
                limit=params.limit,
                offset=params.offset,
                sort_by=params.sort_by,
                sort_order=params.sort_order,
                status=params.status
            )
            
            files_data = [FileDashboardInfo.from_orm(file) for file in files]
            
            return files_data, total_count
            
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve file data: {str(e)}")
    
    async def _calculate_metrics(self, user_id: int) -> UserMetrics:
        """Calculate user metrics and statistics."""
        try:
            metrics_data = await self.repository.calculate_user_metrics(user_id)
            
            if not metrics_data:
                # Return zero metrics if no data found
                return UserMetrics()
            
            return UserMetrics(**metrics_data)
            
        except Exception as e:
            raise MetricsCalculationException(
                f"Failed to calculate user metrics: {str(e)}", 
                user_id=user_id
            )
    
    def _calculate_pagination(
        self, 
        params: DashboardQueryParams, 
        total_count: int
    ) -> PaginationInfo:
        """Calculate pagination information."""
        try:
            # Calculate pagination values
            items_per_page = params.limit
            current_page = (params.offset // params.limit) + 1
            total_pages = (total_count + params.limit - 1) // params.limit  # Ceiling division
            
            has_next = params.offset + params.limit < total_count
            has_previous = params.offset > 0
            
            return PaginationInfo(
                current_page=current_page,
                total_pages=max(total_pages, 1),  # At least 1 page
                total_items=total_count,
                items_per_page=items_per_page,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except Exception as e:
            logger.error(f"Pagination calculation failed: {str(e)}")
            # Return default pagination on error
            return PaginationInfo(
                current_page=1,
                total_pages=1,
                total_items=total_count,
                items_per_page=params.limit,
                has_next=False,
                has_previous=False
            )