# Testing Low-Level Design Document
## GeoPulse Web Application

**Document Version:** 1.0  
**Date:** August 2025  
**Project:** GeoPulse  
**Document Type:** Testing Low-Level Design  

---

## Table of Contents
1. [Testing Strategy](#testing-strategy)
2. [Test Environment Setup](#test-environment-setup)
3. [Unit Testing](#unit-testing)
4. [Integration Testing](#integration-testing)
5. [API Testing](#api-testing)
6. [UI Testing](#ui-testing)
7. [Database Testing](#database-testing)
8. [Performance Testing](#performance-testing)
9. [Security Testing](#security-testing)
10. [Test Data Management](#test-data-management)

---

## Testing Strategy

### Testing Pyramid
```
    E2E Tests (Manual)
        /\
       /  \
   API Tests
      /\
     /  \
Unit Tests
```

### Testing Tools
- **Unit Testing:** pytest (Python), Jest (JavaScript)
- **API Testing:** Postman, pytest-httpx
- **UI Testing:** Manual testing, React Testing Library
- **Database Testing:** pytest with test database
- **Performance Testing:** Locust, Apache Bench
- **Security Testing:** OWASP ZAP, manual security review

---

## Test Environment Setup

### 1. Test Database Configuration
```python
# test_config.py
import os

# Test database configuration
TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/geopulse_test"

# Test file storage
TEST_UPLOAD_DIR = "/tmp/geopulse_test_uploads"

# Test API configuration
TEST_API_BASE_URL = "http://localhost:8000"
TEST_JWT_SECRET = "test_secret_key"
```

### 2. Test Data Setup
```python
# test_data.py
TEST_USERS = [
    {
        "organization_name": "Test Corp",
        "user_name": "John Doe",
        "contact_phone": "1234567890",
        "email": "john@testcorp.com",
        "password": "testpass123"
    },
    {
        "organization_name": "Demo Inc",
        "user_name": "Jane Smith",
        "contact_phone": "0987654321",
        "email": "jane@demoinc.com",
        "password": "demopass456"
    }
]

TEST_FILES = [
    {
        "filename": "test_data.xlsx",
        "engagement_name": "Q1 Analysis",
        "dates": ["2025-01-15", "2025-02-15", "2025-03-15", "2025-04-15"]
    }
]
```

---

## Unit Testing

### 1. Authentication Service Tests

#### Test File: `tests/test_auth_service.py`
```python
import pytest
from unittest.mock import Mock, patch
from app.services.auth_service import AuthService
from app.core.exceptions import AuthenticationException

class TestAuthService:
    """Test cases for authentication service"""
    
    @pytest.fixture
    def auth_service(self, db_session):
        return AuthService(db_session)
    
    @pytest.fixture
    def mock_user_data(self):
        return {
            "organization_name": "Test Corp",
            "user_name": "John Doe",
            "contact_phone": "1234567890",
            "email": "john@testcorp.com",
            "password": "testpass123"
        }
    
    def test_register_user_success(self, auth_service, mock_user_data):
        """Test successful user registration"""
        # Arrange
        user_data = mock_user_data
        
        # Act
        result = auth_service.register_user(user_data)
        
        # Assert
        assert result.user_id is not None
        assert result.email == user_data["email"]
        assert result.user_name == user_data["user_name"]
        assert result.organization_name == user_data["organization_name"]
        assert result.password_hash != user_data["password"]  # Should be hashed
    
    def test_register_user_duplicate_email(self, auth_service, mock_user_data):
        """Test registration with duplicate email"""
        # Arrange
        user_data = mock_user_data
        auth_service.register_user(user_data)  # First registration
        
        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            auth_service.register_user(user_data)  # Second registration
        
        assert "Email already exists" in str(exc_info.value)
        assert exc_info.value.error_code == "E007"
    
    def test_authenticate_user_success(self, auth_service, mock_user_data):
        """Test successful user authentication"""
        # Arrange
        user_data = mock_user_data
        registered_user = auth_service.register_user(user_data)
        
        credentials = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        # Act
        result = auth_service.authenticate_user(credentials)
        
        # Assert
        assert result["access_token"] is not None
        assert result["token_type"] == "bearer"
        assert result["user"]["user_id"] == registered_user.user_id
    
    def test_authenticate_user_invalid_credentials(self, auth_service):
        """Test authentication with invalid credentials"""
        # Arrange
        credentials = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        
        # Act & Assert
        with pytest.raises(AuthenticationException) as exc_info:
            auth_service.authenticate_user(credentials)
        
        assert "Invalid credentials" in str(exc_info.value)
        assert exc_info.value.error_code == "E004"
```

### 2. File Service Tests

#### Test File: `tests/test_file_service.py`
```python
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from app.services.file_service import FileService
from app.core.exceptions import FileProcessingException

class TestFileService:
    """Test cases for file processing service"""
    
    @pytest.fixture
    def file_service(self, db_session):
        return FileService(db_session)
    
    @pytest.fixture
    def mock_file(self):
        """Create a mock file for testing"""
        file_mock = Mock()
        file_mock.filename = "test_data.xlsx"
        file_mock.size = 1024  # 1KB
        file_mock.file = tempfile.NamedTemporaryFile()
        return file_mock
    
    def test_process_file_upload_success(self, file_service, mock_file):
        """Test successful file upload and processing"""
        # Arrange
        user_id = 1
        engagement_name = "Test Engagement"
        dates = ["2025-01-15", "2025-02-15", "2025-03-15", "2025-04-15"]
        
        # Act
        result = file_service.process_file_upload(
            file=mock_file,
            user_id=user_id,
            engagement_name=engagement_name,
            dates=dates
        )
        
        # Assert
        assert result.file_id is not None
        assert result.engagement_name == engagement_name
        assert result.processed_flag == True
        assert result.line_count > 0
        assert os.path.exists(result.storage_location)
    
    def test_process_file_upload_invalid_format(self, file_service):
        """Test file upload with invalid format"""
        # Arrange
        mock_file = Mock()
        mock_file.filename = "test_data.txt"  # Invalid format
        mock_file.size = 1024
        
        # Act & Assert
        with pytest.raises(FileProcessingException) as exc_info:
            file_service.process_file_upload(
                file=mock_file,
                user_id=1,
                engagement_name="Test",
                dates=["2025-01-15", "2025-02-15", "2025-03-15", "2025-04-15"]
            )
        
        assert "Invalid file format" in str(exc_info.value)
        assert exc_info.value.error_code == "E001"
    
    def test_process_file_upload_size_limit(self, file_service):
        """Test file upload exceeding size limit"""
        # Arrange
        mock_file = Mock()
        mock_file.filename = "large_file.xlsx"
        mock_file.size = 100 * 1024 * 1024  # 100MB (exceeds 50MB limit)
        
        # Act & Assert
        with pytest.raises(FileProcessingException) as exc_info:
            file_service.process_file_upload(
                file=mock_file,
                user_id=1,
                engagement_name="Test",
                dates=["2025-01-15", "2025-02-15", "2025-03-15", "2025-04-15"]
            )
        
        assert "File size exceeds limit" in str(exc_info.value)
        assert exc_info.value.error_code == "E002"
```

---

## Integration Testing

### 1. API Integration Tests

#### Test File: `tests/test_api_integration.py`
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
import json

class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    @pytest.fixture
    def client(self, db_session):
        """Create test client with database session"""
        def override_get_db():
            yield db_session
        
        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()
    
    @pytest.fixture
    def auth_token(self, client):
        """Get authentication token for tests"""
        # Register user
        user_data = {
            "organization_name": "Test Corp",
            "user_name": "John Doe",
            "contact_phone": "1234567890",
            "email": "john@testcorp.com",
            "password": "testpass123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Login to get token
        login_data = {
            "username": "john@testcorp.com",
            "password": "testpass123"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        return response.json()["access_token"]
    
    def test_user_registration_flow(self, client):
        """Test complete user registration flow"""
        # Arrange
        user_data = {
            "organization_name": "Test Corp",
            "user_name": "John Doe",
            "contact_phone": "1234567890",
            "email": "john@testcorp.com",
            "password": "testpass123"
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["user_name"] == user_data["user_name"]
        assert "user_id" in data
    
    def test_user_login_flow(self, client):
        """Test complete user login flow"""
        # Arrange
        user_data = {
            "organization_name": "Test Corp",
            "user_name": "John Doe",
            "contact_phone": "1234567890",
            "email": "john@testcorp.com",
            "password": "testpass123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "john@testcorp.com",
            "password": "testpass123"
        }
        
        # Act
        response = client.post("/api/v1/auth/login", data=login_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
    
    def test_file_upload_flow(self, client, auth_token):
        """Test complete file upload flow"""
        # Arrange
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create test file
        test_file_content = b"test,data,content\n1,2,3\n4,5,6"
        files = {"file": ("test_data.csv", test_file_content, "text/csv")}
        data = {
            "engagement_name": "Test Engagement",
            "date1": "2025-01-15",
            "date2": "2025-02-15",
            "date3": "2025-03-15",
            "date4": "2025-04-15"
        }
        
        # Act
        response = client.post(
            "/api/v1/files/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["file_id"] is not None
        assert data["engagement_name"] == "Test Engagement"
        assert data["processed_flag"] == True
    
    def test_dashboard_data_retrieval(self, client, auth_token):
        """Test dashboard data retrieval"""
        # Arrange
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Act
        response = client.get("/api/v1/dashboard", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert "user" in data
        assert isinstance(data["files"], list)
```

---

## API Testing with Postman

### 1. Postman Collection Structure
```
GeoPulse API Tests/
├── Authentication/
│   ├── Register User
│   ├── Login User
│   └── Logout User
├── File Management/
│   ├── Upload File
│   ├── Get File List
│   ├── Get File Details
│   └── Download File
├── Dashboard/
│   ├── Get Dashboard Data
│   └── Get Metrics
└── Error Handling/
    ├── Invalid Credentials
    ├── Invalid File Format
    └── Unauthorized Access
```

### 2. Test Cases with Expected Results

#### Test Case 1: User Registration
**Request:**
```
POST /api/v1/auth/register
Content-Type: application/json

{
    "organization_name": "Test Corp",
    "user_name": "John Doe",
    "contact_phone": "1234567890",
    "email": "john@testcorp.com",
    "password": "testpass123"
}
```

**Expected Response:**
```json
{
    "status": "success",
    "data": {
        "user_id": 1,
        "organization_name": "Test Corp",
        "user_name": "John Doe",
        "contact_phone": "1234567890",
        "email": "john@testcorp.com",
        "created_at": "2025-08-01T10:00:00Z"
    },
    "message": "User registered successfully"
}
```

**Test Steps:**
1. Send registration request
2. Verify status code is 201
3. Verify user_id is generated
4. Verify email is stored correctly
5. Verify password is not returned in response

#### Test Case 2: User Login
**Request:**
```
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=john@testcorp.com&password=testpass123
```

**Expected Response:**
```json
{
    "status": "success",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "user": {
            "user_id": 1,
            "user_name": "John Doe",
            "email": "john@testcorp.com"
        }
    },
    "message": "Login successful"
}
```

**Test Steps:**
1. Send login request with valid credentials
2. Verify status code is 200
3. Verify access_token is returned
4. Verify token_type is "bearer"
5. Verify user information is included

#### Test Case 3: File Upload
**Request:**
```
POST /api/v1/files/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: test_data.xlsx
engagement_name: Q1 Analysis
date1: 2025-01-15
date2: 2025-02-15
date3: 2025-03-15
date4: 2025-04-15
```

**Expected Response:**
```json
{
    "status": "success",
    "data": {
        "file_id": 1,
        "filename": "test_data.xlsx",
        "engagement_name": "Q1 Analysis",
        "upload_date": "2025-08-01",
        "processed_flag": true,
        "line_count": 150,
        "storage_location": "/opt/landrover/1/2025-08-01/output/processed_test_data.xlsx"
    },
    "message": "File uploaded and processed successfully"
}
```

**Test Steps:**
1. Upload valid XLSX file
2. Verify status code is 200
3. Verify file_id is generated
4. Verify processed_flag is true
5. Verify line_count is calculated
6. Verify output file exists

#### Test Case 4: Dashboard Data
**Request:**
```
GET /api/v1/dashboard
Authorization: Bearer <token>
```

**Expected Response:**
```json
{
    "status": "success",
    "data": {
        "user": {
            "user_id": 1,
            "user_name": "John Doe",
            "organization_name": "Test Corp"
        },
        "files": [
            {
                "file_id": 1,
                "filename": "test_data.xlsx",
                "upload_date": "2025-08-01",
                "engagement_name": "Q1 Analysis",
                "processed_flag": true
            }
        ],
        "metrics": {
            "total_files": 1,
            "processed_files": 1,
            "total_lines": 150
        }
    },
    "message": "Dashboard data retrieved successfully"
}
```

**Test Steps:**
1. Request dashboard data with valid token
2. Verify status code is 200
3. Verify user information is included
4. Verify files list is returned
5. Verify metrics are calculated correctly

---

## UI Testing (Manual)

### 1. User Registration Flow
**Test Steps:**
1. Navigate to registration page
2. Fill in all required fields:
   - Organization name: "Test Corp"
   - User name: "John Doe"
   - Contact phone: "1234567890"
   - Email: "john@testcorp.com"
   - Password: "testpass123"
3. Upload organization logo (optional)
4. Click "Register" button
5. Verify success message appears
6. Verify user is redirected to login page

**Expected Results:**
- All form validations work correctly
- Success message: "Registration successful! Please login."
- User is redirected to login page
- User data is stored in database

### 2. User Login Flow
**Test Steps:**
1. Navigate to login page
2. Enter valid credentials:
   - Email: "john@testcorp.com"
   - Password: "testpass123"
3. Click "Login" button
4. Verify successful login
5. Verify user is redirected to dashboard

**Expected Results:**
- Login form validates input
- Success: User is redirected to dashboard
- User logo appears in header
- Navigation tabs are visible

### 3. File Upload Flow
**Test Steps:**
1. Login to application
2. Navigate to "New Upload" tab
3. Drag and drop or select XLSX/CSV file
4. Enter engagement name: "Q1 Analysis"
5. Select 4 dates using date pickers
6. Click "Submit" button
7. Wait for processing to complete
8. Verify success message

**Expected Results:**
- File validation works (only XLSX/CSV accepted)
- Progress indicator shows during upload
- Success message: "File uploaded and processed successfully"
- File appears in transaction history

### 4. Transaction History Flow
**Test Steps:**
1. Navigate to "Past Uploads" tab
2. View list of uploaded files
3. Click on a specific transaction
4. Use search functionality by name
5. Use date range filter
6. Verify file details are displayed

**Expected Results:**
- File list displays correctly
- Search by name works
- Date filtering works
- File details are accurate
- Download option is available

---

## Database Testing

### 1. Database Connection Tests
```python
def test_database_connection():
    """Test database connection and basic operations"""
    from app.database import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1

def test_database_migrations():
    """Test that all migrations can be applied"""
    from alembic import command
    from alembic.config import Config
    
    config = Config("alembic.ini")
    command.upgrade(config, "head")
```

### 2. Data Integrity Tests
```python
def test_user_data_integrity(db_session):
    """Test user data integrity constraints"""
    from app.models.user import User
    
    # Test unique email constraint
    user1 = User(
        organization_name="Test Corp",
        user_name="John Doe",
        contact_phone="1234567890",
        email="john@testcorp.com",
        password_hash="hashed_password"
    )
    db_session.add(user1)
    db_session.commit()
    
    # Try to create user with same email
    user2 = User(
        organization_name="Another Corp",
        user_name="Jane Smith",
        contact_phone="0987654321",
        email="john@testcorp.com",  # Same email
        password_hash="another_hash"
    )
    
    with pytest.raises(Exception):  # Should raise integrity error
        db_session.add(user2)
        db_session.commit()

def test_file_user_relationship(db_session):
    """Test file-user relationship integrity"""
    from app.models.user import User
    from app.models.file import File
    
    # Create user
    user = User(
        organization_name="Test Corp",
        user_name="John Doe",
        contact_phone="1234567890",
        email="john@testcorp.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    
    # Create file for user
    file = File(
        user_id=user.user_id,
        upload_date="2025-08-01",
        filename="test.xlsx",
        original_filename="test.xlsx",
        storage_location="/opt/test.xlsx",
        engagement_name="Test"
    )
    db_session.add(file)
    db_session.commit()
    
    # Verify relationship
    assert file.user.user_id == user.user_id
    assert file.user.email == "john@testcorp.com"
```

---

## Performance Testing

### 1. API Performance Tests
```python
import time
import requests

def test_api_response_time():
    """Test API response times"""
    base_url = "http://localhost:8000"
    
    # Test registration endpoint
    start_time = time.time()
    response = requests.post(f"{base_url}/api/v1/auth/register", json={
        "organization_name": "Test Corp",
        "user_name": "John Doe",
        "contact_phone": "1234567890",
        "email": f"john{time.time()}@testcorp.com",
        "password": "testpass123"
    })
    registration_time = time.time() - start_time
    
    assert response.status_code == 201
    assert registration_time < 2.0  # Should complete within 2 seconds
    
    # Test login endpoint
    start_time = time.time()
    response = requests.post(f"{base_url}/api/v1/auth/login", data={
        "username": f"john{time.time()}@testcorp.com",
        "password": "testpass123"
    })
    login_time = time.time() - start_time
    
    assert response.status_code == 200
    assert login_time < 1.0  # Should complete within 1 second
```

### 2. Database Performance Tests
```python
def test_database_query_performance(db_session):
    """Test database query performance"""
    import time
    from app.models.user import User
    from app.models.file import File
    
    # Create test data
    for i in range(100):
        user = User(
            organization_name=f"Corp {i}",
            user_name=f"User {i}",
            contact_phone=f"123456789{i%10}",
            email=f"user{i}@corp{i}.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        # Add files for each user
        for j in range(10):
            file = File(
                user_id=user.user_id,
                upload_date="2025-08-01",
                filename=f"file{j}.xlsx",
                original_filename=f"file{j}.xlsx",
                storage_location=f"/opt/file{j}.xlsx",
                engagement_name=f"Engagement {j}"
            )
            db_session.add(file)
        db_session.commit()
    
    # Test query performance
    start_time = time.time()
    users = db_session.query(User).all()
    query_time = time.time() - start_time
    
    assert len(users) == 100
    assert query_time < 1.0  # Should complete within 1 second
```

---

## Security Testing

### 1. Authentication Security Tests
```python
def test_jwt_token_security():
    """Test JWT token security"""
    from app.core.security import SecurityManager
    
    security = SecurityManager()
    
    # Test token creation
    token = security.create_access_token({"sub": 1})
    assert token is not None
    
    # Test token verification
    payload = security.verify_token(token)
    assert payload["sub"] == 1
    
    # Test invalid token
    invalid_payload = security.verify_token("invalid_token")
    assert invalid_payload is None

def test_password_security():
    """Test password hashing security"""
    from app.core.security import SecurityManager
    
    security = SecurityManager()
    
    # Test password hashing
    password = "testpass123"
    hashed = security.get_password_hash(password)
    
    assert hashed != password  # Should be hashed
    assert security.verify_password(password, hashed)  # Should verify correctly
    assert not security.verify_password("wrongpassword", hashed)  # Should fail
```

### 2. Input Validation Tests
```python
def test_sql_injection_prevention(client):
    """Test SQL injection prevention"""
    # Test malicious input in registration
    malicious_data = {
        "organization_name": "'; DROP TABLE users; --",
        "user_name": "John Doe",
        "contact_phone": "1234567890",
        "email": "john@testcorp.com",
        "password": "testpass123"
    }
    
    response = client.post("/api/v1/auth/register", json=malicious_data)
    
    # Should not crash and should handle input safely
    assert response.status_code in [201, 400, 422]

def test_xss_prevention(client):
    """Test XSS prevention"""
    # Test malicious input in file upload
    malicious_data = {
        "engagement_name": "<script>alert('xss')</script>",
        "date1": "2025-01-15",
        "date2": "2025-02-15",
        "date3": "2025-03-15",
        "date4": "2025-04-15"
    }
    
    # Should sanitize input and not execute scripts
    # This would be tested in the UI layer
    pass
```

---

## Test Data Management

### 1. Test Data Creation Script
```python
# scripts/create_test_data.py
import asyncio
from app.database import SessionLocal
from app.models.user import User
from app.models.file import File
from app.core.security import SecurityManager
from datetime import date, timedelta

async def create_test_data():
    """Create comprehensive test data"""
    db = SessionLocal()
    security = SecurityManager()
    
    try:
        # Create test users
        users = []
        for i in range(10):
            user = User(
                organization_name=f"Test Corp {i}",
                user_name=f"User {i}",
                contact_phone=f"123456789{i%10}",
                email=f"user{i}@testcorp{i}.com",
                password_hash=security.get_password_hash("testpass123")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            users.append(user)
        
        # Create test files for each user
        for user in users:
            for j in range(5):
                file = File(
                    user_id=user.user_id,
                    upload_date=date.today() - timedelta(days=j),
                    filename=f"test_file_{j}.xlsx",
                    original_filename=f"original_file_{j}.xlsx",
                    line_count=100 + j * 10,
                    storage_location=f"/opt/landrover/{user.user_id}/2025-08-01/input/test_file_{j}.xlsx",
                    processed_flag=True,
                    engagement_name=f"Test Engagement {j}"
                )
                db.add(file)
            db.commit()
        
        print("Test data created successfully!")
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_test_data())
```

### 2. Test Data Cleanup
```python
# scripts/cleanup_test_data.py
from app.database import SessionLocal
from app.models.user import User
from app.models.file import File

def cleanup_test_data():
    """Clean up test data"""
    db = SessionLocal()
    
    try:
        # Delete all test files
        db.query(File).delete()
        
        # Delete all test users
        db.query(User).delete()
        
        db.commit()
        print("Test data cleaned up successfully!")
        
    except Exception as e:
        print(f"Error cleaning up test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_test_data()
```

---

## Test Execution Commands

### 1. Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth_service.py

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### 2. Test Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    slow: Slow running tests
```

---

## Next Steps for Developers

1. **Set up test environment** - Install testing tools and configure test database
2. **Write unit tests** - Start with service layer tests
3. **Create integration tests** - Test API endpoints and database operations
4. **Set up automated testing** - Configure CI/CD pipeline
5. **Implement UI tests** - Create manual test cases and automated UI tests
6. **Add performance tests** - Test API response times and database performance
7. **Conduct security testing** - Test authentication and input validation
8. **Create test data** - Set up comprehensive test data sets
9. **Monitor test coverage** - Ensure adequate test coverage
10. **Maintain test suite** - Keep tests updated with code changes

Remember to:
- Write tests before or alongside code (TDD approach)
- Aim for 90%+ code coverage
- Test both happy path and error scenarios
- Use meaningful test names and descriptions
- Keep tests independent and isolated
- Use appropriate test data and fixtures
- Document test cases and expected results
- Run tests regularly in CI/CD pipeline
