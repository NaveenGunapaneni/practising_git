"""Upload module services."""

import os
import time
import shutil
from pathlib import Path
from datetime import datetime, date
from typing import List, Optional
from fastapi import UploadFile

from app.modules.upload.repository import UploadRepository
from app.modules.upload.processors.core_processor import CoreFileProcessor
from app.modules.upload.processors.real_sentinel_hub_processor import RealSentinelHubProcessor
from app.modules.upload.processors.file_validator import FileValidator
from app.modules.upload.processors.excel_formatter import format_environmental_analysis_excel
from app.modules.upload.schemas import FileUploadRequest, FileUploadData
from app.config import settings
from app.core.exceptions import FileUploadException, FileProcessingException, StorageException
from app.core.logger import get_logger

logger = get_logger(__name__)


class UploadService:
    """Service for handling file uploads and processing workflow."""
    
    def __init__(
        self, 
        repository: UploadRepository,
        processor: CoreFileProcessor,
        validator: FileValidator,
        sentinel_hub_processor: RealSentinelHubProcessor = None
    ):
        self.repository = repository
        self.processor = processor
        self.validator = validator
        self.sentinel_hub_processor = sentinel_hub_processor or RealSentinelHubProcessor()
        self.upload_dir = Path(settings.upload_dir)
        self.temp_dir = Path(settings.upload_temp_dir)
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure upload and temp directories exist."""
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directories ensured: {self.upload_dir}, {self.temp_dir}")
        except Exception as e:
            raise StorageException(f"Failed to create directories: {str(e)}")
    
    def _create_user_directories(self, user_id: int, upload_date: date) -> tuple[Path, Path]:
        """Create user-specific directory structure with timestamp for unique transactions."""
        try:
            # Create timestamp-based directory for unique transactions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            user_dir = self.upload_dir / str(user_id) / timestamp
            
            input_dir = user_dir / "input"
            output_dir = user_dir / "output"
            
            input_dir.mkdir(parents=True, exist_ok=True)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Created directories for user {user_id}: {input_dir}, {output_dir}")
            return input_dir, output_dir
            
        except Exception as e:
            raise StorageException(f"Failed to create user directories: {str(e)}")
    
    async def _store_file(self, file: UploadFile, input_dir: Path) -> Path:
        """Store uploaded file in the input directory."""
        try:
            # Generate unique filename to prevent conflicts
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = input_dir / filename
            
            # Write file content
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Reset file position for potential re-reading
            await file.seek(0)
            
            logger.info(f"File stored: {file_path}")
            return file_path
            
        except Exception as e:
            raise StorageException(f"Failed to store file: {str(e)}")
    
    async def _is_geospatial_data(self, file_path: Path) -> bool:
        """Determine if the file contains geospatial data based on column names."""
        try:
            if file_path.suffix.lower() == '.csv':
                import pandas as pd
                df = pd.read_csv(file_path, nrows=1)  # Read only header
                columns = [col.lower() for col in df.columns]
                
                # Check for geospatial indicators
                geospatial_indicators = [
                    'latitude', 'longitude', 'easting', 'northing', 
                    'point_id', 'lp_no', 'extent_ac'
                ]
                
                # If file has geospatial coordinate columns, treat as geospatial
                has_coordinates = any(indicator in ' '.join(columns) for indicator in geospatial_indicators)
                
                logger.info(f"Geospatial detection - columns: {columns}, has_coordinates: {has_coordinates}")
                return has_coordinates
                
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                import pandas as pd
                df = pd.read_excel(file_path, nrows=1)
                columns = [col.lower() for col in df.columns]
                
                geospatial_indicators = [
                    'latitude', 'longitude', 'easting', 'northing', 
                    'point_id', 'lp_no', 'extent_ac'
                ]
                
                has_coordinates = any(indicator in ' '.join(columns) for indicator in geospatial_indicators)
                return has_coordinates
                
            return False
            
        except Exception as e:
            logger.warning(f"Failed to detect geospatial data type: {str(e)}")
            return False  # Default to generic processing
    
    async def _count_file_lines(self, file_path: Path) -> int:
        """Count lines in the uploaded file."""
        try:
            if file_path.suffix.lower() == '.csv':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return sum(1 for _ in f) - 1  # Subtract header row
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                import pandas as pd
                df = pd.read_excel(file_path)
                return len(df)
            else:
                return 0
        except Exception as e:
            logger.warning(f"Failed to count lines in {file_path}: {str(e)}")
            return 0
    
    async def upload_and_process_file(
        self,
        file: UploadFile,
        request: FileUploadRequest,
        user_id: int,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> FileUploadData:
        """Main workflow for file upload and processing."""
        
        logger.info(f"Starting file upload for user {user_id}: {file.filename}")
        
        try:
            # Step 1: Validate file
            await self.validator.validate_file(file)
            
            # Step 2: Create directory structure
            upload_date = date.today()
            input_dir, output_dir = self._create_user_directories(user_id, upload_date)
            
            # Step 3: Store file
            input_path = await self._store_file(file, input_dir)
            
            # Step 4: Calculate file size
            file_size_mb = input_path.stat().st_size / (1024 * 1024)
            
            # Step 5: Create database record
            file_record = await self.repository.create_file_record(
                user_id=user_id,
                filename=input_path.name,
                original_filename=file.filename,
                input_location=str(input_path),
                engagement_name=request.engagement_name,
                dates=[request.date1, request.date2, request.date3, request.date4],
                file_size_mb=file_size_mb,
                browser_ip=client_ip
            )
            
            logger.info(f"File record created: {file_record.file_id}")
            
            # Step 6: Process file
            try:
                processing_start = time.time()
                
                # Determine if this is geospatial data based on column names
                is_geospatial = await self._is_geospatial_data(input_path)
                
                if is_geospatial:
                    logger.info(f"Processing as geospatial data with real Sentinel Hub API: {input_path}")
                    output_path = await self.sentinel_hub_processor.process_file(
                        input_path=input_path,
                        output_dir=output_dir,
                        dates=[request.date1, request.date2, request.date3, request.date4],
                        engagement_name=request.engagement_name
                    )
                else:
                    logger.info(f"Processing as generic data: {input_path}")
                    output_path = await self.processor.process_file(
                        input_path=input_path,
                        output_dir=output_dir,
                        dates=[request.date1, request.date2, request.date3, request.date4],
                        engagement_name=request.engagement_name
                    )
                
                # Create formatted Excel file if output is CSV
                if output_path.suffix.lower() == '.csv':
                    try:
                        logger.info(f"Creating formatted Excel file from: {output_path}")
                        excel_path = format_environmental_analysis_excel(output_path)
                        logger.info(f"Formatted Excel file created: {excel_path}")
                        # Update output_path to point to the Excel file for database storage
                        output_path = excel_path
                    except Exception as e:
                        logger.warning(f"Failed to create formatted Excel file: {str(e)}")
                        # Continue with CSV file if Excel formatting fails
                
                processing_time = time.time() - processing_start
                
                # Step 7: Count lines and update database
                line_count = await self._count_file_lines(input_path)
                
                updated_record = await self.repository.update_processing_results(
                    file_id=file_record.file_id,
                    storage_location=str(output_path),
                    processed_flag=True,
                    processing_time_seconds=processing_time,
                    line_count=line_count
                )
                
                logger.info(f"File processing completed: {file_record.file_id} in {processing_time:.2f}s")
                
                # Step 8: Create response data
                return FileUploadData(
                    file_id=updated_record.file_id,
                    filename=updated_record.filename,
                    original_filename=updated_record.original_filename,
                    engagement_name=updated_record.engagement_name,
                    upload_date=updated_record.upload_date.isoformat(),
                    processed_flag=updated_record.processed_flag,
                    line_count=updated_record.line_count,
                    storage_location=updated_record.storage_location,
                    input_location=updated_record.input_location,
                    processing_time_seconds=float(updated_record.processing_time_seconds) if updated_record.processing_time_seconds else None,
                    file_size_mb=float(updated_record.file_size_mb),
                    dates=updated_record.dates,
                    created_at=updated_record.created_at,
                    updated_at=updated_record.updated_at
                )
                
            except Exception as e:
                # Mark processing as failed
                await self.repository.update_processing_results(
                    file_id=file_record.file_id,
                    processed_flag=False,
                    error_message=str(e)
                )
                
                logger.error(f"File processing failed for {file_record.file_id}: {str(e)}")
                raise FileProcessingException(f"File processing failed: {str(e)}", file_record.file_id)
                
        except (FileUploadException, FileProcessingException, StorageException):
            # Re-raise known exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {str(e)}")
            raise FileUploadException(f"File upload failed: {str(e)}", file.filename, user_id)
    
    async def get_user_files(self, user_id: int, limit: int = 100, offset: int = 0) -> List[FileUploadData]:
        """Get all files for a user."""
        try:
            files = await self.repository.get_files_by_user(user_id, limit, offset)
            
            return [
                FileUploadData(
                    file_id=f.file_id,
                    filename=f.filename,
                    original_filename=f.original_filename,
                    engagement_name=f.engagement_name,
                    upload_date=f.upload_date.isoformat(),
                    processed_flag=f.processed_flag,
                    line_count=f.line_count,
                    storage_location=f.storage_location,
                    input_location=f.input_location,
                    processing_time_seconds=float(f.processing_time_seconds) if f.processing_time_seconds else None,
                    file_size_mb=float(f.file_size_mb),
                    dates=f.dates,
                    created_at=f.created_at,
                    updated_at=f.updated_at
                )
                for f in files
            ]
            
        except Exception as e:
            logger.error(f"Failed to get user files: {str(e)}")
            raise FileUploadException(f"Failed to retrieve files: {str(e)}", user_id=user_id)
    
    async def get_file_status(self, file_id: int, user_id: int) -> Optional[FileUploadData]:
        """Get file status by ID."""
        try:
            file_record = await self.repository.get_file_by_id(file_id, user_id)
            
            if not file_record:
                return None
            
            return FileUploadData(
                file_id=file_record.file_id,
                filename=file_record.filename,
                original_filename=file_record.original_filename,
                engagement_name=file_record.engagement_name,
                upload_date=file_record.upload_date.isoformat(),
                processed_flag=file_record.processed_flag,
                line_count=file_record.line_count,
                storage_location=file_record.storage_location,
                input_location=file_record.input_location,
                processing_time_seconds=float(file_record.processing_time_seconds) if file_record.processing_time_seconds else None,
                file_size_mb=float(file_record.file_size_mb),
                dates=file_record.dates,
                created_at=file_record.created_at,
                updated_at=file_record.updated_at
            )
            
        except Exception as e:
            logger.error(f"Failed to get file status: {str(e)}")
            raise FileUploadException(f"Failed to get file status: {str(e)}", user_id=user_id)
    
    async def download_file(self, file_id: int, user_id: int):
        """Download a processed file."""
        try:
            # Get file record and verify ownership
            file_record = await self.repository.get_file_by_id(file_id, user_id)
            
            if not file_record:
                raise FileUploadException(f"File not found: {file_id}", user_id=user_id)
            
            if not file_record.processed_flag:
                raise FileUploadException(f"File not yet processed: {file_id}", user_id=user_id)
            
            # Construct the output file path
            output_path = Path(file_record.storage_location)
            
            if not output_path.exists():
                raise FileUploadException(f"Processed file not found on disk: {output_path}", user_id=user_id)
            
            # Return file information for download
            return {
                "file_path": str(output_path),
                "filename": file_record.filename,
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "file_size": output_path.stat().st_size
            }
            
        except FileUploadException:
            # Re-raise known exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to prepare file download: {str(e)}")
            raise FileUploadException(f"Failed to prepare file download: {str(e)}", user_id=user_id)