"""Tests for file upload service."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
from datetime import date
from fastapi import UploadFile

from app.modules.upload.services import UploadService
from app.modules.upload.processors.core_processor import CoreFileProcessor
from app.modules.upload.processors.file_validator import FileValidator
from app.modules.upload.repository import UploadRepository
from app.modules.upload.schemas import FileUploadRequest
from app.modules.upload.config import UploadConfig
from app.shared.models.base import File
from app.core.exceptions import FileUploadException, FileProcessingException


class TestFileUploadService:
    """Test cases for FileUploadService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock file repository."""
        return Mock(spec=FileRepository)
    
    @pytest.fixture
    def mock_processor(self):
        """Mock file processor."""
        return Mock(spec=FileProcessorService)
    
    @pytest.fixture
    def mock_validator(self):
        """Mock file validator."""
        return Mock(spec=FileValidatorService)
    
    @pytest.fixture
    def upload_service(self, mock_repository, mock_processor, mock_validator):
        """Create UploadService instance with mocked dependencies."""
        config = UploadConfig()
        config.UPLOAD_DIR = "/tmp/test_uploads"
        config.TEMP_DIR = "/tmp/test_temp"
        
        with patch('pathlib.Path.mkdir'):
            return UploadService(
                repository=mock_repository,
                processor=mock_processor,
                validator=mock_validator,
                config=config
            )
    
    @pytest.fixture
    def mock_file(self):
        """Mock uploaded file."""
        file = Mock(spec=UploadFile)
        file.filename = "test.xlsx"
        file.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        file.size = 1024 * 1024  # 1MB
        file.read = AsyncMock(return_value=b"test file content")
        file.seek = AsyncMock()
        return file
    
    @pytest.fixture
    def upload_request(self):
        """Mock upload request."""
        return FileUploadRequest(
            engagement_name="Test Engagement",
            date1="2025-01-15",
            date2="2025-02-15",
            date3="2025-03-15",
            date4="2025-04-15"
        )
    
    @pytest.fixture
    def mock_file_record(self):
        """Mock file database record."""
        file_record = Mock(spec=File)
        file_record.file_id = 123
        file_record.filename = "test.xlsx"
        file_record.original_filename = "test.xlsx"
        file_record.engagement_name = "Test Engagement"
        file_record.upload_date = date.today()
        file_record.processed_flag = True
        file_record.line_count = 100
        file_record.storage_location = "/tmp/test_uploads/1/2025-01-15/output/processed_test.xlsx"
        file_record.input_location = "/tmp/test_uploads/1/2025-01-15/input/test.xlsx"
        file_record.processing_time_seconds = 45.2
        file_record.file_size_mb = 1.0
        file_record.dates = ["2025-01-15", "2025-02-15", "2025-03-15", "2025-04-15"]
        file_record.created_at = "2025-01-15T10:30:00Z"
        file_record.updated_at = "2025-01-15T10:35:00Z"
        return file_record
    
    @pytest.mark.asyncio
    async def test_upload_and_process_file_success(
        self, 
        upload_service, 
        mock_file, 
        upload_request, 
        mock_file_record,
        mock_repository,
        mock_processor,
        mock_validator
    ):
        """Test successful file upload and processing."""
        
        # Setup mocks
        mock_validator.validate_file = AsyncMock()
        mock_repository.create_file_record = AsyncMock(return_value=mock_file_record)
        mock_repository.update_processing_results = AsyncMock(return_value=mock_file_record)
        mock_processor.process_file = AsyncMock(return_value=Path("/tmp/output/processed_test.xlsx"))
        
        with patch('pathlib.Path.mkdir'), \
             patch('builtins.open'), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch.object(upload_service, '_count_file_lines', return_value=100):
            
            mock_stat.return_value.st_size = 1024 * 1024  # 1MB
            
            # Execute
            result = await upload_service.upload_and_process_file(
                file=mock_file,
                request=upload_request,
                user_id=1,
                client_ip="192.168.1.1"
            )
            
            # Verify
            assert result.file_id == 123
            assert result.filename == "test.xlsx"
            assert result.processed_flag is True
            assert result.engagement_name == "Test Engagement"
            
            # Verify service calls
            mock_validator.validate_file.assert_called_once_with(mock_file)
            mock_repository.create_file_record.assert_called_once()
            mock_processor.process_file.assert_called_once()
            mock_repository.update_processing_results.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_file_validation_failure(
        self, 
        upload_service, 
        mock_file, 
        upload_request,
        mock_validator
    ):
        """Test file upload with validation failure."""
        
        # Setup mock to raise validation exception
        mock_validator.validate_file = AsyncMock(
            side_effect=FileUploadException("Invalid file format", mock_file.filename)
        )
        
        # Execute and verify exception
        with pytest.raises(FileUploadException) as exc_info:
            await upload_service.upload_and_process_file(
                file=mock_file,
                request=upload_request,
                user_id=1,
                client_ip="192.168.1.1"
            )
        
        assert "Invalid file format" in str(exc_info.value)
        mock_validator.validate_file.assert_called_once_with(mock_file)
    
    @pytest.mark.asyncio
    async def test_upload_file_processing_failure(
        self, 
        upload_service, 
        mock_file, 
        upload_request, 
        mock_file_record,
        mock_repository,
        mock_processor,
        mock_validator
    ):
        """Test file upload with processing failure."""
        
        # Setup mocks
        mock_validator.validate_file = AsyncMock()
        mock_repository.create_file_record = AsyncMock(return_value=mock_file_record)
        mock_repository.update_processing_results = AsyncMock()
        mock_processor.process_file = AsyncMock(
            side_effect=FileProcessingException("Processing failed", mock_file_record.file_id)
        )
        
        with patch('pathlib.Path.mkdir'), \
             patch('builtins.open'), \
             patch('pathlib.Path.stat') as mock_stat:
            
            mock_stat.return_value.st_size = 1024 * 1024  # 1MB
            
            # Execute and verify exception
            with pytest.raises(FileProcessingException) as exc_info:
                await upload_service.upload_and_process_file(
                    file=mock_file,
                    request=upload_request,
                    user_id=1,
                    client_ip="192.168.1.1"
                )
            
            assert "Processing failed" in str(exc_info.value)
            
            # Verify that processing failure was recorded
            mock_repository.update_processing_results.assert_called_with(
                file_id=mock_file_record.file_id,
                processed_flag=False,
                error_message="Processing failed"
            )
    
    @pytest.mark.asyncio
    async def test_get_user_files(
        self, 
        upload_service, 
        mock_repository
    ):
        """Test getting user files."""
        
        # Setup mock
        mock_files = [Mock(spec=File) for _ in range(3)]
        for i, mock_file in enumerate(mock_files):
            mock_file.file_id = i + 1
            mock_file.filename = f"test_{i+1}.xlsx"
            mock_file.original_filename = f"test_{i+1}.xlsx"
            mock_file.engagement_name = f"Engagement {i+1}"
            mock_file.upload_date = date.today()
            mock_file.processed_flag = True
            mock_file.line_count = 100
            mock_file.storage_location = f"/tmp/output/test_{i+1}.xlsx"
            mock_file.input_location = f"/tmp/input/test_{i+1}.xlsx"
            mock_file.processing_time_seconds = 45.2
            mock_file.file_size_mb = 1.0
            mock_file.dates = ["2025-01-15", "2025-02-15", "2025-03-15", "2025-04-15"]
            mock_file.created_at = "2025-01-15T10:30:00Z"
            mock_file.updated_at = "2025-01-15T10:35:00Z"
        
        mock_repository.get_files_by_user = AsyncMock(return_value=mock_files)
        
        # Execute
        result = await upload_service.get_user_files(user_id=1, limit=10, offset=0)
        
        # Verify
        assert len(result) == 3
        assert all(file_data.file_id in [1, 2, 3] for file_data in result)
        mock_repository.get_files_by_user.assert_called_once_with(1, 10, 0)
    
    @pytest.mark.asyncio
    async def test_get_file_status_found(
        self, 
        upload_service, 
        mock_file_record,
        mock_repository
    ):
        """Test getting file status when file exists."""
        
        # Setup mock
        mock_repository.get_file_by_id = AsyncMock(return_value=mock_file_record)
        
        # Execute
        result = await upload_service.get_file_status(file_id=123, user_id=1)
        
        # Verify
        assert result is not None
        assert result.file_id == 123
        assert result.filename == "test.xlsx"
        mock_repository.get_file_by_id.assert_called_once_with(123, 1)
    
    @pytest.mark.asyncio
    async def test_get_file_status_not_found(
        self, 
        upload_service, 
        mock_repository
    ):
        """Test getting file status when file doesn't exist."""
        
        # Setup mock
        mock_repository.get_file_by_id = AsyncMock(return_value=None)
        
        # Execute
        result = await upload_service.get_file_status(file_id=999, user_id=1)
        
        # Verify
        assert result is None
        mock_repository.get_file_by_id.assert_called_once_with(999, 1)