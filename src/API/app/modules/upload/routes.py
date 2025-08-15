"""Upload module API routes."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.modules.upload.schemas import (
    FileUploadRequest, FileUploadResponse, FileListResponse, FileStatusResponse
)
from app.modules.upload.services import UploadService
from app.modules.upload.repository import UploadRepository
from app.modules.upload.processors.core_processor import CoreFileProcessor
from app.modules.upload.processors.real_sentinel_hub_processor import RealSentinelHubProcessor
from app.modules.upload.processors.file_validator import FileValidator
from app.config import settings
from app.shared.utils.security import get_current_user
from app.modules.upload.models import User
from app.core.exceptions import (
    FileUploadException, FileProcessingException, StorageException, 
    ValidationException, AuthenticationException
)
from app.core.error_handler import ErrorHandler
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP and user agent from request."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return client_ip, user_agent


@router.post("/upload", response_model=FileUploadResponse, status_code=200)
async def upload_file(
    request: Request,
    file: UploadFile = File(..., description="XLSX or CSV file to upload (max 50MB)"),
    engagement_name: str = Form(..., description="Engagement name"),
    date1: str = Form(..., description="Date 1 (YYYY-MM-DD)"),
    date2: str = Form(..., description="Date 2 (YYYY-MM-DD)"),
    date3: str = Form(..., description="Date 3 (YYYY-MM-DD)"),
    date4: str = Form(..., description="Date 4 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Upload and process XLSX/CSV files with engagement details.
    
    This endpoint handles file upload with the following workflow:
    1. Authenticate user via JWT token
    2. Validate file format, size, and security
    3. Store file in user-specific directory structure
    4. Create database record with file metadata
    5. Process file with core business logic
    6. Generate processed output file with conditional formatting
    7. Update database with processing results
    
    **Authentication Required:** JWT Bearer token in Authorization header
    
    **File Requirements:**
    - Format: XLSX or CSV only
    - Size: Maximum 50MB
    - Content: Valid spreadsheet data
    
    **Form Data Fields:**
    - file: The file to upload
    - engagement_name: Name of the engagement (max 255 chars)
    - date1, date2, date3, date4: Dates in YYYY-MM-DD format
    
    **Response:** File processing results with metadata and storage locations
    """
    
    try:
        # Get authenticated user
        user_id = current_user.user_id
        client_ip, user_agent = get_client_info(request)
        
        logger.info(f"File upload request from user {user_id}: {file.filename}")
        
        # Create request object for validation
        upload_request = FileUploadRequest(
            engagement_name=engagement_name,
            date1=date1,
            date2=date2,
            date3=date3,
            date4=date4
        )
        
        # Initialize services
        upload_repository = UploadRepository(db)
        file_processor = CoreFileProcessor()
        sentinel_hub_processor = RealSentinelHubProcessor()
        file_validator = FileValidator(
            max_file_size_mb=settings.MAX_FILE_SIZE_MB,
            allowed_extensions=settings.ALLOWED_FILE_TYPES,
            allowed_mime_types=settings.ALLOWED_MIME_TYPES
        )
        
        upload_service = UploadService(
            repository=upload_repository,
            processor=file_processor,
            validator=file_validator,
            sentinel_hub_processor=sentinel_hub_processor
        )
        
        # Process file upload
        result = await upload_service.upload_and_process_file(
            file=file,
            request=upload_request,
            user_id=user_id,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        logger.info(f"File upload completed successfully: {result.file_id}")
        
        return FileUploadResponse(
            data=result,
            message="File uploaded and processed successfully",
            timestamp=datetime.utcnow()
        )
        
    except AuthenticationException as e:
        logger.warning(f"Authentication failed for file upload: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
        
    except FileUploadException as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "E001",
                "message": str(e),
                "details": {
                    "filename": getattr(e, 'filename', None),
                    "user_id": getattr(e, 'user_id', None)
                }
            }
        )
        
    except FileProcessingException as e:
        logger.error(f"File processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "E005",
                "message": str(e),
                "details": {
                    "file_id": getattr(e, 'file_id', None),
                    "operation": getattr(e, 'operation', None)
                }
            }
        )
        
    except StorageException as e:
        logger.error(f"Storage operation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "E006",
                "message": str(e),
                "details": {
                    "path": getattr(e, 'path', None)
                }
            }
        )
        
    except ValidationException as e:
        logger.error(f"Validation failed: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail={
                "error_code": "E007",
                "message": str(e),
                "details": {
                    "field": getattr(e, 'field', None),
                    "value": getattr(e, 'value', None)
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during file upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "E000",
                "message": "Internal server error",
                "details": {"error": str(e)}
            }
        )


@router.get("/list", response_model=FileListResponse, status_code=200)
async def list_user_files(
    request: Request,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List all files uploaded by the authenticated user.
    
    **Authentication Required:** JWT Bearer token in Authorization header
    
    **Query Parameters:**
    - limit: Maximum number of files to return (default: 100)
    - offset: Number of files to skip for pagination (default: 0)
    
    **Response:** List of user's uploaded files with metadata
    """
    
    try:
        # Get authenticated user
        user_id = current_user.user_id
        
        logger.info(f"File list request from user {user_id}")
        
        # Initialize services
        upload_repository = UploadRepository(db)
        file_processor = CoreFileProcessor()
        file_validator = FileValidator()
        
        upload_service = UploadService(
            repository=upload_repository,
            processor=file_processor,
            validator=file_validator
        )
        
        # Get user files
        files = await upload_service.get_user_files(user_id, limit, offset)
        
        return FileListResponse(
            data=files,
            message=f"Retrieved {len(files)} files",
            timestamp=datetime.utcnow()
        )
        
    except AuthenticationException as e:
        logger.warning(f"Authentication failed for file list: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
        
    except Exception as e:
        logger.error(f"Error retrieving file list: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "E000",
                "message": "Failed to retrieve files",
                "details": {"error": str(e)}
            }
        )


@router.get("/status/{file_id}", response_model=FileStatusResponse, status_code=200)
async def get_file_status(
    file_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get the status and details of a specific file.
    
    **Authentication Required:** JWT Bearer token in Authorization header
    
    **Path Parameters:**
    - file_id: ID of the file to check
    
    **Response:** File status and processing details
    """
    
    try:
        # Get authenticated user
        user_id = current_user.user_id
        
        logger.info(f"File status request from user {user_id} for file {file_id}")
        
        # Initialize services
        upload_repository = UploadRepository(db)
        file_processor = CoreFileProcessor()
        file_validator = FileValidator()
        
        upload_service = UploadService(
            repository=upload_repository,
            processor=file_processor,
            validator=file_validator
        )
        
        # Get file status
        file_data = await upload_service.get_file_status(file_id, user_id)
        
        if not file_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "E404",
                    "message": "File not found",
                    "details": {"file_id": file_id}
                }
            )
        
        return FileStatusResponse(
            data=file_data,
            message="File status retrieved successfully",
            timestamp=datetime.utcnow()
        )
        
    except AuthenticationException as e:
        logger.warning(f"Authentication failed for file status: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error retrieving file status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "E000",
                "message": "Failed to retrieve file status",
                "details": {"error": str(e)}
            }
        )


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Download processed file."""
    try:
        # Get current user ID from JWT token
        user_id = get_current_user_id(request)
        
        logger.info(f"File download request from user {user_id} for file {file_id}")
        
        # Initialize services
        upload_repository = UploadRepository(db)
        file_processor = CoreFileProcessor()
        file_validator = FileValidator()
        
        upload_service = UploadService(
            repository=upload_repository,
            processor=file_processor,
            validator=file_validator
        )
        
        # Get file information for download
        file_info = await upload_service.download_file(file_id, user_id)
        
        # Read file content
        with open(file_info["file_path"], "rb") as f:
            file_content = f.read()
        
        # Return file as response
        return Response(
            content=file_content,
            media_type=file_info["content_type"],
            headers={
                "Content-Disposition": f"attachment; filename={file_info['filename']}",
                "Content-Length": str(file_info["file_size"])
            }
        )
        
    except AuthenticationException as e:
        logger.warning(f"Authentication failed for file download: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "E000",
                "message": "Failed to download file",
                "details": {"error": str(e)}
            }
        )
@router.post("/test-upload")
async def test_upload(
    request: Request,
    file: UploadFile = File(...),
    engagement_name: str = Form(...),
    date1: str = Form(...),
    date2: str = Form(...),
    date3: str = Form(...),
    date4: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Test endpoint to debug form data reception."""
    try:
        return {
            "status": "success",
            "data": {
                "user_id": current_user.user_id,
                "filename": file.filename,
                "file_size": file.size,
                "content_type": file.content_type,
                "engagement_name": engagement_name,
                "date1": date1,
                "date2": date2,
                "date3": date3,
                "date4": date4
            },
            "message": "Test upload successful"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }