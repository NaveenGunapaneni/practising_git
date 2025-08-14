"""Upload module repository."""

from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.modules.upload.models import File, User
from app.core.exceptions import DatabaseException


class UploadRepository:
    """Repository for file upload database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_file_record(
        self,
        user_id: int,
        filename: str,
        original_filename: str,
        input_location: str,
        engagement_name: str,
        dates: List[str],
        file_size_mb: float,
        browser_ip: Optional[str] = None,
        browser_location: Optional[str] = None
    ) -> File:
        """Create a new file record in the database."""
        try:
            file_record = File(
                user_id=user_id,
                upload_date=date.today(),
                filename=filename,
                original_filename=original_filename,
                input_location=input_location,
                storage_location=input_location,  # Initially same as input
                engagement_name=engagement_name,
                dates=dates,
                file_size_mb=file_size_mb,
                browser_ip=browser_ip,
                browser_location=browser_location,
                processed_flag=False
            )
            
            self.db.add(file_record)
            await self.db.commit()
            await self.db.refresh(file_record)
            
            return file_record
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to create file record: {str(e)}")
    
    async def update_processing_results(
        self,
        file_id: int,
        storage_location: Optional[str] = None,
        processed_flag: Optional[bool] = None,
        processing_time_seconds: Optional[float] = None,
        line_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> File:
        """Update file record with processing results."""
        try:
            update_data = {"updated_at": datetime.utcnow()}
            
            if storage_location is not None:
                update_data["storage_location"] = storage_location
            if processed_flag is not None:
                update_data["processed_flag"] = processed_flag
            if processing_time_seconds is not None:
                update_data["processing_time_seconds"] = processing_time_seconds
            if line_count is not None:
                update_data["line_count"] = line_count
            if error_message is not None:
                update_data["error_message"] = error_message
            
            stmt = update(File).where(File.file_id == file_id).values(**update_data)
            await self.db.execute(stmt)
            await self.db.commit()
            
            # Fetch and return updated record
            result = await self.db.execute(
                select(File).where(File.file_id == file_id)
            )
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                raise DatabaseException(f"File record not found: {file_id}")
            
            return file_record
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to update file record: {str(e)}")
    
    async def get_file_by_id(self, file_id: int, user_id: int) -> Optional[File]:
        """Get file record by ID and user ID."""
        try:
            result = await self.db.execute(
                select(File)
                .where(File.file_id == file_id)
                .where(File.user_id == user_id)
                .options(selectinload(File.user))
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            raise DatabaseException(f"Failed to get file record: {str(e)}")
    
    async def get_files_by_user(self, user_id: int, limit: int = 100, offset: int = 0) -> List[File]:
        """Get all files for a user with pagination."""
        try:
            result = await self.db.execute(
                select(File)
                .where(File.user_id == user_id)
                .order_by(File.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
            
        except Exception as e:
            raise DatabaseException(f"Failed to get user files: {str(e)}")
    
    async def delete_file_record(self, file_id: int, user_id: int) -> bool:
        """Delete file record by ID and user ID."""
        try:
            result = await self.db.execute(
                select(File)
                .where(File.file_id == file_id)
                .where(File.user_id == user_id)
            )
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                return False
            
            await self.db.delete(file_record)
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseException(f"Failed to delete file record: {str(e)}")
    
    async def get_processing_status(self, file_id: int, user_id: int) -> Optional[dict]:
        """Get file processing status."""
        try:
            result = await self.db.execute(
                select(File.file_id, File.processed_flag, File.error_message, File.processing_time_seconds)
                .where(File.file_id == file_id)
                .where(File.user_id == user_id)
            )
            row = result.first()
            
            if not row:
                return None
            
            return {
                "file_id": row.file_id,
                "processed_flag": row.processed_flag,
                "error_message": row.error_message,
                "processing_time_seconds": float(row.processing_time_seconds) if row.processing_time_seconds else None
            }
            
        except Exception as e:
            raise DatabaseException(f"Failed to get processing status: {str(e)}")