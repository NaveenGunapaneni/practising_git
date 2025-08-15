"""Unit tests for file service."""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from datetime import datetime

from app.services.file_service import FileService
from app.shared.models.base import User
from app.core.exceptions import FileSystemException, ValidationException


class TestFileService:
    """Test cases for FileService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Use temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.file_service = FileService(base_path=self.temp_dir)
        
        # Create mock user
        self.mock_user = MagicMock(spec=User)
        self.mock_user.user_id = 123
        self.mock_user.organization_name = "Test Corp"
        self.mock_user.user_name = "John Doe"
        self.mock_user.contact_phone = "1234567890"
        self.mock_user.email = "john@testcorp.com"
        self.mock_user.logo_path = "/defaults/datalegos.png"
        self.mock_user.created_at = datetime(2025, 8, 11, 10, 30, 0)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_create_user_json_success(self):
        """Test successful user JSON file creation."""
        file_path = await self.file_service.create_user_json(self.mock_user)
        
        # Check file was created
        assert Path(file_path).exists()
        assert file_path.endswith("john_doe.json")
        
        # Check file contents
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["user_id"] == 123
        assert data["organization_name"] == "Test Corp"
        assert data["user_name"] == "John Doe"
        assert data["email"] == "john@testcorp.com"
        assert "password_hash" not in data  # Should be excluded
        assert data["created_at"] == "2025-08-11T10:30:00"
    
    @pytest.mark.asyncio
    async def test_create_user_json_invalid_user(self):
        """Test create_user_json with invalid user data."""
        # Test with None user
        with pytest.raises(ValidationException) as exc_info:
            await self.file_service.create_user_json(None)
        
        assert "Invalid user data" in str(exc_info.value)
        
        # Test with user without user_name
        invalid_user = MagicMock(spec=User)
        invalid_user.user_name = None
        
        with pytest.raises(ValidationException) as exc_info:
            await self.file_service.create_user_json(invalid_user)
        
        assert "Invalid user data" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_user_json_special_characters(self):
        """Test JSON creation with special characters in user name."""
        self.mock_user.user_name = "John O'Connor-Smith Jr."
        
        file_path = await self.file_service.create_user_json(self.mock_user)
        
        # Check safe filename was created
        assert Path(file_path).exists()
        assert "john_o_connor_smith_jr.json" in file_path
    
    def test_validate_logo_path_valid(self):
        """Test logo path validation with valid paths."""
        valid_paths = [
            "/uploads/logos/logo.png",
            "/defaults/datalegos.png",
            "images/company_logo.jpg",
            "",  # Empty path should be valid
            None  # None should be handled gracefully
        ]
        
        for path in valid_paths:
            if path is not None:
                assert self.file_service.validate_logo_path(path) is True
    
    def test_validate_logo_path_directory_traversal(self):
        """Test logo path validation rejects directory traversal."""
        invalid_paths = [
            "../../../etc/passwd",
            "~/secret_file",
            "/uploads/../../../etc/passwd",
            "images/../../config.json"
        ]
        
        for path in invalid_paths:
            with pytest.raises(ValidationException) as exc_info:
                self.file_service.validate_logo_path(path)
            
            assert "directory traversal not allowed" in str(exc_info.value)
    
    def test_validate_logo_path_invalid_characters(self):
        """Test logo path validation rejects invalid characters."""
        invalid_paths = [
            "/uploads/logo<script>.png",
            "/uploads/logo|rm -rf.png",
            "/uploads/logo;cat /etc/passwd.png",
            "/uploads/logo`whoami`.png"
        ]
        
        for path in invalid_paths:
            with pytest.raises(ValidationException) as exc_info:
                self.file_service.validate_logo_path(path)
            
            assert "invalid characters" in str(exc_info.value)
    
    def test_validate_logo_path_too_long(self):
        """Test logo path validation rejects paths that are too long."""
        long_path = "/uploads/" + "a" * 500 + ".png"
        
        with pytest.raises(ValidationException) as exc_info:
            self.file_service.validate_logo_path(long_path)
        
        assert "too long" in str(exc_info.value)
    
    def test_create_safe_filename(self):
        """Test safe filename creation."""
        test_cases = [
            ("John Doe", "john_doe"),
            ("John O'Connor-Smith Jr.", "john_o_connor_smith_jr"),
            ("User@Company.com", "user_company_com"),
            ("   Multiple   Spaces   ", "multiple_spaces"),
            ("", "user"),  # Empty name should default to "user"
            ("A" * 150, "a" * 100),  # Long names should be truncated
        ]
        
        for input_name, expected in test_cases:
            result = self.file_service._create_safe_filename(input_name)
            assert result == expected
    
    @pytest.mark.asyncio
    async def test_file_exists(self):
        """Test file existence checking."""
        # Create a test file
        test_file = Path(self.temp_dir) / "test_file.json"
        test_file.write_text('{"test": "data"}')
        
        # Test existing file
        assert await self.file_service.file_exists("test_file.json") is True
        
        # Test non-existing file
        assert await self.file_service.file_exists("nonexistent.json") is False
    
    @pytest.mark.asyncio
    async def test_delete_user_json_success(self):
        """Test successful user JSON file deletion."""
        # First create a file
        await self.file_service.create_user_json(self.mock_user)
        
        # Verify file exists
        assert await self.file_service.file_exists("john_doe.json") is True
        
        # Delete the file
        result = await self.file_service.delete_user_json("John Doe")
        
        # Verify deletion
        assert result is True
        assert await self.file_service.file_exists("john_doe.json") is False
    
    @pytest.mark.asyncio
    async def test_delete_user_json_nonexistent(self):
        """Test deleting non-existent user JSON file."""
        result = await self.file_service.delete_user_json("Nonexistent User")
        
        # Should return False for non-existent file
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_directory_access_success(self):
        """Test successful directory access check."""
        result = await self.file_service.check_directory_access()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_directory_access_failure(self):
        """Test directory access check failure."""
        # Use an invalid path
        invalid_service = FileService(base_path="/invalid/readonly/path")
        result = await invalid_service.check_directory_access()
        
        # Should return False for inaccessible directory
        assert result is False