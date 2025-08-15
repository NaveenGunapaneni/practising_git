"""Unit tests for user repository."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.modules.registration.repository import RegistrationRepository as UserRepository
from app.shared.models.base import User
from app.modules.registration.schemas import UserRegistrationRequest as UserCreate
from app.core.exceptions import DatabaseException, DuplicateEmailException


class TestUserRepository:
    """Test cases for UserRepository."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.repository = UserRepository(self.mock_session)
        
        # Sample user data
        self.user_data = UserCreate(
            organization_name="Test Corp",
            user_name="John Doe",
            contact_phone="1234567890",
            email="john@testcorp.com",
            password_hash="$2b$12$hashed_password",
            logo_path="/defaults/datalegos.png"
        )
    
    @pytest.mark.asyncio
    async def test_email_exists_true(self):
        """Test email_exists returns True when email exists."""
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar.return_value = 123  # User ID exists
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.email_exists("john@testcorp.com")
        
        assert result is True
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_email_exists_false(self):
        """Test email_exists returns False when email doesn't exist."""
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar.return_value = None  # No user found
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.email_exists("nonexistent@testcorp.com")
        
        assert result is False
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_email_exists_database_error(self):
        """Test email_exists raises DatabaseException on database error."""
        self.mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(DatabaseException) as exc_info:
            await self.repository.email_exists("john@testcorp.com")
        
        assert "Failed to check email existence" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Test successful user creation."""
        # Mock successful database operations
        self.mock_session.add = MagicMock()
        self.mock_session.flush = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        result = await self.repository.create_user(self.user_data)
        
        assert isinstance(result, User)
        assert result.email == self.user_data.email
        assert result.organization_name == self.user_data.organization_name
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self):
        """Test create_user raises DuplicateEmailException for duplicate email."""
        # Mock integrity error for duplicate email
        integrity_error = IntegrityError("", "", "unique constraint failed: users.email")
        self.mock_session.flush.side_effect = integrity_error
        
        with pytest.raises(DuplicateEmailException) as exc_info:
            await self.repository.create_user(self.user_data)
        
        assert self.user_data.email in str(exc_info.value)
        self.mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_database_error(self):
        """Test create_user raises DatabaseException on database error."""
        self.mock_session.flush.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(DatabaseException) as exc_info:
            await self.repository.create_user(self.user_data)
        
        assert "Failed to create user" in str(exc_info.value)
        self.mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self):
        """Test get_user_by_id returns user when found."""
        # Mock user found
        mock_user = User(user_id=123, email="john@testcorp.com")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.get_user_by_id(123)
        
        assert result == mock_user
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Test get_user_by_id returns None when not found."""
        # Mock user not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.get_user_by_id(999)
        
        assert result is None
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self):
        """Test get_user_by_email returns user when found."""
        # Mock user found
        mock_user = User(user_id=123, email="john@testcorp.com")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        self.mock_session.execute.return_value = mock_result
        
        result = await self.repository.get_user_by_email("john@testcorp.com")
        
        assert result == mock_user
        self.mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_commit_success(self):
        """Test successful transaction commit."""
        self.mock_session.commit = AsyncMock()
        
        await self.repository.commit()
        
        self.mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_commit_failure(self):
        """Test commit raises DatabaseException on failure."""
        self.mock_session.commit.side_effect = SQLAlchemyError("Commit failed")
        
        with pytest.raises(DatabaseException) as exc_info:
            await self.repository.commit()
        
        assert "Failed to commit transaction" in str(exc_info.value)
        self.mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rollback_success(self):
        """Test successful transaction rollback."""
        self.mock_session.rollback = AsyncMock()
        
        await self.repository.rollback()
        
        self.mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rollback_failure(self):
        """Test rollback raises DatabaseException on failure."""
        self.mock_session.rollback.side_effect = SQLAlchemyError("Rollback failed")
        
        with pytest.raises(DatabaseException) as exc_info:
            await self.repository.rollback()
        
        assert "Failed to rollback transaction" in str(exc_info.value)