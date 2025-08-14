"""Dashboard repository for database operations."""

from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from sqlalchemy.orm import selectinload
from datetime import datetime, date

from app.modules.upload.models import File, User
from app.core.exceptions import DatabaseException
from app.core.logger import get_logger

logger = get_logger(__name__)


class DashboardRepository:
    """Repository for dashboard-related database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_dashboard_info(self, user_id: int) -> Optional[User]:
        """
        Retrieve user information for dashboard display.
        
        Args:
            user_id: ID of the user
            
        Returns:
            User object with dashboard-relevant information
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            result = await self.db.execute(
                select(User)
                .where(User.user_id == user_id)
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Failed to retrieve user dashboard info for user {user_id}: {str(e)}")
            raise DatabaseException(f"Failed to retrieve user information: {str(e)}")
    
    async def get_user_files_paginated(
        self,
        user_id: int,
        limit: int,
        offset: int,
        sort_by: str,
        sort_order: str,
        status: str
    ) -> Tuple[List[File], int]:
        """
        Retrieve user files with filtering, sorting, and pagination.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of files to return
            offset: Number of files to skip
            sort_by: Field to sort by (upload_date, filename, engagement_name)
            sort_order: Sort order (asc, desc)
            status: Filter by status (all, processed, pending)
            
        Returns:
            Tuple of (files list, total count)
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            # Build base query with user filter
            base_query = select(File).where(File.user_id == user_id)
            
            # Apply status filtering
            if status == "processed":
                base_query = base_query.where(File.processed_flag == True)
            elif status == "pending":
                base_query = base_query.where(File.processed_flag == False)
            # For "all", no additional filtering needed
            
            # Apply sorting
            sort_column = getattr(File, sort_by)
            if sort_order == "desc":
                base_query = base_query.order_by(sort_column.desc())
            else:
                base_query = base_query.order_by(sort_column.asc())
            
            # Get total count for pagination
            count_query = select(func.count(File.file_id)).where(File.user_id == user_id)
            if status == "processed":
                count_query = count_query.where(File.processed_flag == True)
            elif status == "pending":
                count_query = count_query.where(File.processed_flag == False)
            
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar()
            
            # Apply pagination and execute query
            paginated_query = base_query.limit(limit).offset(offset)
            result = await self.db.execute(paginated_query)
            files = result.scalars().all()
            
            return files, total_count
            
        except Exception as e:
            logger.error(f"Failed to retrieve user files for user {user_id}: {str(e)}")
            raise DatabaseException(f"Failed to retrieve user files: {str(e)}")
    
    async def calculate_user_metrics(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Calculate comprehensive user metrics and statistics.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary containing all calculated metrics
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            # Single query to calculate all metrics efficiently
            metrics_query = select(
                func.count(File.file_id).label('total_files'),
                func.sum(case((File.processed_flag == True, 1), else_=0)).label('processed_files'),
                func.sum(case((File.processed_flag == False, 1), else_=0)).label('pending_files'),
                func.coalesce(func.sum(File.line_count), 0).label('total_lines'),
                func.coalesce(func.avg(File.line_count), 0).label('average_lines_per_file'),
                func.sum(
                    case(
                        (File.upload_date >= func.date_trunc('month', func.current_date()), 1),
                        else_=0
                    )
                ).label('files_this_month'),
                func.sum(
                    case(
                        (File.upload_date >= func.date_trunc('week', func.current_date()), 1),
                        else_=0
                    )
                ).label('files_this_week'),
                func.coalesce(func.sum(File.file_size_mb), 0).label('storage_used_mb')
            ).where(File.user_id == user_id)
            
            result = await self.db.execute(metrics_query)
            row = result.first()
            
            if not row or row.total_files == 0:
                # Return zero metrics if no files found
                return {
                    'total_files': 0,
                    'processed_files': 0,
                    'pending_files': 0,
                    'total_lines': 0,
                    'average_lines_per_file': 0.0,
                    'files_this_month': 0,
                    'files_this_week': 0,
                    'storage_used_mb': 0.0
                }
            
            return {
                'total_files': int(row.total_files or 0),
                'processed_files': int(row.processed_files or 0),
                'pending_files': int(row.pending_files or 0),
                'total_lines': int(row.total_lines or 0),
                'average_lines_per_file': float(row.average_lines_per_file or 0.0),
                'files_this_month': int(row.files_this_month or 0),
                'files_this_week': int(row.files_this_week or 0),
                'storage_used_mb': float(row.storage_used_mb or 0.0)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate user metrics for user {user_id}: {str(e)}")
            raise DatabaseException(f"Failed to calculate user metrics: {str(e)}")