"""Unit tests for password service."""

import pytest
from app.services.password_service import PasswordService
from app.core.exceptions import ValidationException


class TestPasswordService:
    """Test cases for PasswordService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.password_service = PasswordService(salt_rounds=4)  # Lower rounds for faster tests
    
    def test_hash_password_success(self):
        """Test successful password hashing."""
        password = "testpassword123"
        hashed = self.password_service.hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Ensure it's actually hashed
        assert hashed.startswith('$2b$')  # bcrypt format
    
    def test_hash_password_empty(self):
        """Test hashing empty password raises exception."""
        with pytest.raises(ValidationException) as exc_info:
            self.password_service.hash_password("")
        
        assert exc_info.value.error_code == "E007"
        assert "cannot be empty" in exc_info.value.message
        assert exc_info.value.field == "password"
    
    def test_hash_password_too_short(self):
        """Test hashing password that's too short."""
        with pytest.raises(ValidationException) as exc_info:
            self.password_service.hash_password("12345")
        
        assert exc_info.value.error_code == "E007"
        assert "at least 6 characters" in exc_info.value.message
        assert exc_info.value.field == "password"
    
    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "testpassword123"
        hashed = self.password_service.hash_password(password)
        
        assert self.password_service.verify_password(password, hashed) is True
    
    def test_verify_password_wrong_password(self):
        """Test password verification with wrong password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = self.password_service.hash_password(password)
        
        assert self.password_service.verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_inputs(self):
        """Test password verification with empty inputs."""
        assert self.password_service.verify_password("", "hash") is False
        assert self.password_service.verify_password("password", "") is False
        assert self.password_service.verify_password("", "") is False
    
    def test_verify_password_invalid_hash(self):
        """Test password verification with invalid hash."""
        password = "testpassword123"
        invalid_hash = "invalid_hash_format"
        
        assert self.password_service.verify_password(password, invalid_hash) is False
    
    def test_validate_password_strength_success(self):
        """Test successful password strength validation."""
        valid_passwords = [
            "123456",  # Minimum length
            "testpassword",
            "P@ssw0rd123!",
            "a" * 255  # Maximum length
        ]
        
        for password in valid_passwords:
            assert self.password_service.validate_password_strength(password) is True
    
    def test_validate_password_strength_empty(self):
        """Test password strength validation with empty password."""
        with pytest.raises(ValidationException) as exc_info:
            self.password_service.validate_password_strength("")
        
        assert exc_info.value.error_code == "E007"
        assert "required" in exc_info.value.message
    
    def test_validate_password_strength_too_short(self):
        """Test password strength validation with short password."""
        with pytest.raises(ValidationException) as exc_info:
            self.password_service.validate_password_strength("12345")
        
        assert exc_info.value.error_code == "E007"
        assert "at least 6 characters" in exc_info.value.message
    
    def test_validate_password_strength_too_long(self):
        """Test password strength validation with long password."""
        long_password = "a" * 256
        
        with pytest.raises(ValidationException) as exc_info:
            self.password_service.validate_password_strength(long_password)
        
        assert exc_info.value.error_code == "E007"
        assert "less than 255 characters" in exc_info.value.message
    
    def test_different_salt_rounds(self):
        """Test that different salt rounds produce different hashes."""
        password = "testpassword123"
        service1 = PasswordService(salt_rounds=4)
        service2 = PasswordService(salt_rounds=6)
        
        hash1 = service1.hash_password(password)
        hash2 = service2.hash_password(password)
        
        # Hashes should be different due to different salts
        assert hash1 != hash2
        
        # But both should verify correctly
        assert service1.verify_password(password, hash1) is True
        assert service2.verify_password(password, hash2) is True