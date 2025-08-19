"""Upload module API routes."""

from datetime import datetime
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Response
from fastapi.responses import HTMLResponse
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
            user_agent=user_agent,
            db_session=db
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Download processed file."""
    try:
        # Get current user ID from authenticated user
        user_id = current_user.user_id
        
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


@router.get("/{file_id}/view")
async def view_html_results(
    file_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """View HTML results of processed file."""
    try:
        # Get current user ID from authenticated user
        user_id = current_user.user_id
        
        logger.info(f"HTML view request from user {user_id} for file {file_id}")
        
        # Initialize services
        upload_repository = UploadRepository(db)
        file_processor = CoreFileProcessor()
        file_validator = FileValidator()
        
        upload_service = UploadService(
            repository=upload_repository,
            processor=file_processor,
            validator=file_validator
        )
        
        # Get file information for HTML view
        file_info = await upload_service.get_html_file(file_id, user_id)
        
        # Read HTML file content
        with open(file_info["html_path"], "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Return HTML as response
        return HTMLResponse(
            content=html_content,
            headers={
                "Content-Type": "text/html; charset=utf-8"
            }
        )
        
    except AuthenticationException as e:
        logger.warning(f"Authentication failed for HTML view: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error viewing HTML results: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "E000",
                "message": "Failed to view HTML results",
                "details": {"error": str(e)}
            }
        )

@router.get("/{file_id}/view-demo")
async def view_html_results_demo(
    file_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """View HTML results of processed file for demo mode (no authentication required)."""
    try:
        logger.info(f"Demo HTML view request for file {file_id}")
        
        # For demo mode, we'll use a hardcoded user ID (13) and file path
        # This is a temporary solution for demo purposes
        
        # Construct the expected file path for demo
        demo_file_path = f"./user_data/uploads/13/20250819_200853/output/20250819_200908_batch_analysis_before20250101_20250701.csv"
        csv_path = Path(demo_file_path)
        html_path = csv_path.with_suffix('.html')
        
        if not csv_path.exists():
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "E404",
                    "message": "Demo CSV file not found",
                    "details": {"file_path": str(csv_path)}
                }
            )
        
        # Generate new HTML format on-the-fly for demo
        import pandas as pd
        from app.modules.upload.processors.real_sentinel_hub_processor import RealSentinelHubProcessor
        
        # Read the CSV data with proper encoding handling
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                # Try with different CSV parsing options
                df = pd.read_csv(
                    csv_path, 
                    encoding=encoding,
                    on_bad_lines='skip',  # Skip problematic lines
                    engine='python',  # Use python engine for better error handling
                    quoting=3  # QUOTE_NONE - disable quote parsing
                )
                logger.info(f"Successfully read demo CSV with encoding: {encoding}")
                break
            except (UnicodeDecodeError, pd.errors.ParserError) as e:
                logger.warning(f"Failed to read demo CSV with encoding {encoding}: {str(e)}")
                continue
        
        # If still failed, try with more aggressive error handling
        if df is None:
            for encoding in encodings:
                try:
                    df = pd.read_csv(
                        csv_path, 
                        encoding=encoding,
                        on_bad_lines='skip',
                        engine='python',
                        quoting=3,
                        sep=None,  # Let pandas detect separator
                        error_bad_lines=False,  # Skip bad lines
                        warn_bad_lines=False
                    )
                    logger.info(f"Successfully read demo CSV with fallback options and encoding: {encoding}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to read demo CSV with fallback options and encoding {encoding}: {str(e)}")
                    continue
        
        if df is None:
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "E500",
                    "message": "Failed to read demo CSV file with any supported encoding or parsing options",
                    "details": {"file_path": str(csv_path)}
                }
            )
        
        # Generate new HTML with the specified column requirements
        processor = RealSentinelHubProcessor()
        processor._generate_new_html_output(df, html_path, "Demo Engagement")
        
        if not html_path.exists():
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "E500",
                    "message": "Failed to generate demo HTML file",
                    "details": {"file_path": str(html_path)}
                }
            )
        
        # Read HTML file content
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Return HTML as response
        return HTMLResponse(
            content=html_content,
            headers={
                "Content-Type": "text/html; charset=utf-8"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error viewing demo HTML results: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "E000",
                "message": "Failed to view demo HTML results",
                "details": {"error": str(e)}
            }
        )
@router.get("/debug/columns/{file_id}")
async def debug_file_columns(file_id: int, current_user: User = Depends(get_current_user)):
    """Debug endpoint to inspect the actual columns in a CSV file."""
    try:
        logger.info(f"Debugging columns for file ID: {file_id}")
        
        # Get the file record
        file_record = await file_service.get_file_by_id(file_id, current_user.id)
        if not file_record:
            raise FileUploadException(f"File not found: {file_id}", user_id=current_user.id)
        
        # Construct the correct CSV file path (not the Excel file path)
        # The storage_location points to the Excel file, but we need the CSV file
        excel_path = Path(file_record.storage_location)
        
        # Convert Excel path to CSV path
        if excel_path.suffix.lower() == '.xlsx':
            output_path = excel_path.with_suffix('.csv')
        else:
            output_path = excel_path
        
        logger.info(f"Looking for CSV file at: {output_path}")
        
        if not output_path.exists():
            raise FileUploadException(f"CSV file not found: {output_path}", user_id=current_user.id)
        
        # Read the CSV file with robust encoding handling
        import pandas as pd
        
        # Try different encodings to handle the file properly
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(
                    output_path, 
                    encoding=encoding,
                    on_bad_lines='skip',
                    engine='python',
                    quoting=3
                )
                logger.info(f"Successfully read CSV with encoding: {encoding}")
                break
            except (UnicodeDecodeError, pd.errors.ParserError) as e:
                logger.warning(f"Failed to read CSV with encoding {encoding}: {str(e)}")
                continue
        
        if df is None:
            raise FileUploadException(f"Failed to read CSV file with any supported encoding", user_id=current_user.id)
        
        # Analyze the columns
        actual_columns = list(df.columns)
        total_columns = len(actual_columns)
        
        # Check for expected columns
        expected_basic = ['lp_no', 'extent_ac', 'POINT_ID', 'EASTING-X', 'NORTHING-Y', 'LATITUDE', 'LONGITUDE']
        expected_period = ['Before Period Start', 'Before Period End', 'After Period Start', 'After Period End']
        expected_interpretation = ['Vegetation (NDVI)-Interpretation', 'Built-up Area (NDBI)-Interpretation', 'Water/Moisture (NDWI)-Interpretation']
        expected_significance = ['Vegetation (NDVI)-Significance', 'Built-up Area (NDBI)-Significance', 'Water/Moisture (NDWI)-Significance']
        
        found_basic = [col for col in expected_basic if col in actual_columns]
        found_period = [col for col in expected_period if col in actual_columns]
        found_interpretation = [col for col in expected_interpretation if col in actual_columns]
        found_significance = [col for col in expected_significance if col in actual_columns]
        
        # Look for similar columns
        similar_columns = {}
        for expected in expected_basic + expected_period + expected_interpretation + expected_significance:
            similar = []
            for actual in actual_columns:
                if any(keyword.lower() in actual.lower() for keyword in expected.lower().split()):
                    similar.append(actual)
            if similar:
                similar_columns[expected] = similar
        
        # Create detailed analysis
        analysis = {
            "file_id": file_id,
            "filename": file_record.filename,
            "total_columns": total_columns,
            "actual_columns": actual_columns,
            "column_analysis": {
                "basic_columns": {
                    "expected": expected_basic,
                    "found": found_basic,
                    "missing": [col for col in expected_basic if col not in actual_columns]
                },
                "period_columns": {
                    "expected": expected_period,
                    "found": found_period,
                    "missing": [col for col in expected_period if col not in actual_columns]
                },
                "interpretation_columns": {
                    "expected": expected_interpretation,
                    "found": found_interpretation,
                    "missing": [col for col in expected_interpretation if col not in actual_columns]
                },
                "significance_columns": {
                    "expected": expected_significance,
                    "found": found_significance,
                    "missing": [col for col in expected_significance if col not in actual_columns]
                }
            },
            "similar_columns": similar_columns,
            "sample_data": {
                "shape": df.shape,
                "first_few_rows": df.head(3).to_dict('records') if len(df) > 0 else []
            }
        }
        
        logger.info(f"Column analysis completed for file {file_id}")
        return {"status": "success", "data": analysis}
        
    except Exception as e:
        logger.error(f"Error debugging file columns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error debugging file columns: {str(e)}")
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