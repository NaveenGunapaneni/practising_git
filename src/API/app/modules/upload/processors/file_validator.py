"""File validation processor for upload security."""

from pathlib import Path
from typing import List, Set
from fastapi import UploadFile

from app.core.exceptions import FileUploadException, ValidationException
from app.core.logger import get_logger

# Optional import for python-magic
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

logger = get_logger(__name__)


class FileValidator:
    """Service for validating uploaded files."""
    
    def __init__(
        self,
        max_file_size_mb: int = 50,
        allowed_extensions: List[str] = None,
        allowed_mime_types: List[str] = None
    ):
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.max_file_size_mb = max_file_size_mb
        
        self.allowed_extensions = set(allowed_extensions or ['.xlsx', '.csv', '.xls'])
        self.allowed_mime_types = set(allowed_mime_types or [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
            'application/vnd.ms-excel',  # .xls
            'text/csv',  # .csv
            'application/csv',  # .csv alternative
            'application/octet-stream',  # Generic binary (for CSV files)
            'text/plain'  # Plain text (for CSV files)
        ])
    
    async def validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file for security and format compliance."""
        
        logger.info(f"Validating file: {file.filename}")
        
        # Check if file is provided
        if not file or not file.filename:
            raise FileUploadException("No file provided", file.filename if file else None)
        
        # Validate file extension
        self._validate_file_extension(file.filename)
        
        # Validate file size
        await self._validate_file_size(file)
        
        # Validate MIME type
        await self._validate_mime_type(file)
        
        # Additional security checks
        await self._security_checks(file)
        
        logger.info(f"File validation passed: {file.filename}")
    
    def _validate_file_extension(self, filename: str) -> None:
        """Validate file extension."""
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        
        if extension not in self.allowed_extensions:
            raise FileUploadException(
                f"Invalid file format. Only {', '.join(self.allowed_extensions)} files are allowed.",
                filename
            )
    
    async def _validate_file_size(self, file: UploadFile) -> None:
        """Validate file size."""
        # Read file content to check size
        content = await file.read()
        file_size = len(content)
        
        # Reset file position
        await file.seek(0)
        
        if file_size > self.max_file_size_bytes:
            file_size_mb = file_size / (1024 * 1024)
            raise FileUploadException(
                f"File size exceeds maximum limit of {self.max_file_size_mb}MB. "
                f"File size: {file_size_mb:.2f}MB",
                file.filename
            )
        
        logger.debug(f"File size validation passed: {file_size / (1024 * 1024):.2f}MB")
    
    async def _validate_mime_type(self, file: UploadFile) -> None:
        """Validate MIME type using python-magic if available, otherwise use content-type header."""
        try:
            # Get file extension for additional validation
            file_extension = Path(file.filename).suffix.lower()
            
            if HAS_MAGIC:
                # Read first 2048 bytes for MIME type detection
                content = await file.read(2048)
                await file.seek(0)
                
                # Detect MIME type
                mime_type = magic.from_buffer(content, mime=True)
                
                # Special handling for CSV files which might be detected as text/plain
                if file_extension == '.csv' and mime_type in ['text/plain', 'application/octet-stream']:
                    # For CSV files, check if content looks like CSV
                    content_str = content.decode('utf-8', errors='ignore')
                    if ',' in content_str or ';' in content_str:
                        logger.debug(f"CSV file detected by extension and content validation: {file.filename}")
                        return  # Accept CSV file
                
                # Check if MIME type is allowed
                if mime_type not in self.allowed_mime_types:
                    # Also check the content-type header as fallback
                    if file.content_type not in self.allowed_mime_types:
                        # Special case for CSV files with generic MIME types
                        if file_extension == '.csv' and mime_type in ['text/plain', 'application/octet-stream']:
                            logger.debug(f"Accepting CSV file with generic MIME type: {mime_type}")
                            return
                        
                        raise FileUploadException(
                            f"Invalid file type. Detected MIME type: {mime_type}. "
                            f"Allowed types: {', '.join(self.allowed_mime_types)}",
                            file.filename
                        )
                
                logger.debug(f"MIME type validation passed: {mime_type}")
            else:
                # Fallback to content-type header when python-magic is not available
                logger.debug("python-magic not available, using content-type header for validation")
                
                # Special handling for CSV files
                if file_extension == '.csv' and file.content_type in ['application/octet-stream', 'text/plain']:
                    logger.debug(f"Accepting CSV file with generic content-type: {file.content_type}")
                    return
                
                if file.content_type not in self.allowed_mime_types:
                    raise FileUploadException(
                        f"Invalid file type. Content-Type: {file.content_type}. "
                        f"Allowed types: {', '.join(self.allowed_mime_types)}",
                        file.filename
                    )
                
                logger.debug(f"Content-Type validation passed: {file.content_type}")
            
        except Exception as e:
            if isinstance(e, FileUploadException):
                raise
            logger.warning(f"MIME type validation failed, using content-type header: {str(e)}")
            
            # Final fallback - be more lenient with CSV files
            file_extension = Path(file.filename).suffix.lower()
            if file_extension == '.csv':
                logger.debug(f"Accepting CSV file based on extension: {file.filename}")
                return
            
            # Final fallback to content-type header
            if file.content_type not in self.allowed_mime_types:
                raise FileUploadException(
                    f"Invalid file type. Content-Type: {file.content_type}. "
                    f"Allowed types: {', '.join(self.allowed_mime_types)}",
                    file.filename
                )
    
    async def _security_checks(self, file: UploadFile) -> None:
        """Perform additional security checks."""
        
        # Check for suspicious filenames
        self._check_suspicious_filename(file.filename)
        
        # Check file content for basic structure validation
        await self._validate_file_structure(file)
    
    def _check_suspicious_filename(self, filename: str) -> None:
        """Check for suspicious filename patterns."""
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            raise FileUploadException(
                "Filename contains invalid characters",
                filename
            )
        
        # Check for executable extensions (security)
        dangerous_extensions = {'.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js', '.jar'}
        file_path = Path(filename)
        
        if file_path.suffix.lower() in dangerous_extensions:
            raise FileUploadException(
                "Executable files are not allowed",
                filename
            )
        
        # Check filename length
        if len(filename) > 255:
            raise FileUploadException(
                "Filename is too long (max 255 characters)",
                filename
            )
    
    async def _validate_file_structure(self, file: UploadFile) -> None:
        """Validate basic file structure."""
        try:
            # Read a small portion of the file to check structure
            content = await file.read(1024)
            await file.seek(0)
            
            filename = file.filename.lower()
            
            if filename.endswith('.csv'):
                # Basic CSV validation - check for common CSV patterns
                content_str = content.decode('utf-8', errors='ignore')
                if not content_str.strip():
                    raise FileUploadException("CSV file appears to be empty", file.filename)
                
                # Check for common CSV delimiters
                if ',' not in content_str and ';' not in content_str and '\t' not in content_str:
                    logger.warning(f"CSV file may not have standard delimiters: {file.filename}")
            
            elif filename.endswith(('.xlsx', '.xls')):
                # Basic Excel validation - check for Excel file signatures
                excel_signatures = [
                    b'PK\x03\x04',  # XLSX (ZIP-based)
                    b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1',  # XLS (OLE2)
                ]
                
                if not any(content.startswith(sig) for sig in excel_signatures):
                    raise FileUploadException(
                        "File does not appear to be a valid Excel file",
                        file.filename
                    )
            
            logger.debug(f"File structure validation passed: {file.filename}")
            
        except UnicodeDecodeError:
            # This is expected for binary files like Excel
            pass
        except FileUploadException:
            raise
        except Exception as e:
            logger.warning(f"File structure validation warning: {str(e)}")
            # Don't fail on structure validation errors, just log them
    
    def validate_engagement_name(self, engagement_name: str) -> str:
        """Validate engagement name."""
        if not engagement_name or not engagement_name.strip():
            raise ValidationException("Engagement name is required", "engagement_name", engagement_name)
        
        engagement_name = engagement_name.strip()
        
        if len(engagement_name) > 255:
            raise ValidationException(
                "Engagement name is too long (max 255 characters)",
                "engagement_name",
                engagement_name
            )
        
        return engagement_name
    
    def validate_dates(self, dates: List[str]) -> List[str]:
        """Validate date formats."""
        from datetime import datetime
        
        validated_dates = []
        
        for i, date_str in enumerate(dates, 1):
            if not date_str:
                raise ValidationException(f"Date {i} is required", f"date{i}", date_str)
            
            try:
                # Validate date format
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                validated_dates.append(date_str)
            except ValueError:
                raise ValidationException(
                    f"Invalid date format for date {i}. Use YYYY-MM-DD",
                    f"date{i}",
                    date_str
                )
        
        return validated_dates