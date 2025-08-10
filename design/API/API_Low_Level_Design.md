# API Low-Level Design Document
## GeoPulse Web Application

**Document Version:** 1.0  
**Date:** August 2025  
**Project:** GeoPulse  
**Document Type:** API Low-Level Design  

---

## Table of Contents
1. [Technology Stack](#technology-stack)
2. [Project Structure](#project-structure)
3. [API Architecture](#api-architecture)
4. [Database Models](#database-models)
5. [API Endpoints](#api-endpoints)
6. [Authentication & Security](#authentication--security)
7. [File Processing Workflow](#file-processing-workflow)
8. [Error Handling](#error-handling)
9. [Configuration Management](#configuration-management)
10. [Development Setup](#development-setup)

---

## Technology Stack

### Backend Technologies
- **Framework:** FastAPI 0.104.x
- **Language:** Python 3.11+
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0+
- **Authentication:** JWT (PyJWT)
- **File Processing:** pandas, openpyxl
- **Validation:** Pydantic
- **Testing:** pytest, httpx
- **Documentation:** Swagger/OpenAPI

### Development Tools
- **IDE:** VS Code with Python extensions
- **API Testing:** Postman
- **Database GUI:** pgAdmin
- **Version Control:** Git

---

## Project Structure

```
geopulse-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── file.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── file.py
│   │   └── auth.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── files.py
│   │   │   └── dashboard.py
│   │   └── deps.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── config.py
│   │   └── exceptions.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── file_service.py
│   │   └── processing_service.py
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_files.py
├── alembic/
│   ├── versions/
│   └── alembic.ini
├── requirements.txt
├── environment.yml
├── environment_auth.yml
├── environment_file.yml
└── README.md
```

---

## API Architecture

### Main Application (`app/main.py`)
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.database import engine, Base
from app.api.v1 import auth, users, files, dashboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting GeoPulse API...")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    logger.info("Shutting down GeoPulse API...")

app = FastAPI(
    title="GeoPulse API",
    description="File processing and analytics API",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    return {"message": "Welcome to GeoPulse API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## Database Models

### User Model (`app/models/user.py`)
```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    organization_name = Column(String(255), nullable=False)
    user_name = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    logo_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email})>"
```

### File Model (`app/models/file.py`)
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class File(Base):
    __tablename__ = "files"
    
    file_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    upload_date = Column(Date, nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    line_count = Column(Integer, nullable=True)
    storage_location = Column(String(500), nullable=False)
    processed_flag = Column(Boolean, default=False)
    engagement_name = Column(String(255), nullable=True)
    browser_ip = Column(String(45), nullable=True)
    browser_location = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="files")
    
    def __repr__(self):
        return f"<File(file_id={self.file_id}, filename={self.filename})>"
```

---

## API Endpoints

### 1. Authentication Endpoints (`app/api/v1/auth.py`)

#### User Registration
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token
from app.services.auth_service import AuthService
from app.core.exceptions import CustomException
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    Args:
        user_data: User registration data
        db: Database session
    
    Returns:
        UserResponse: Created user information
    
    Raises:
        HTTPException: If email already exists or validation fails
    """
    try:
        logger.info(f"Attempting to register user with email: {user_data.email}")
        
        auth_service = AuthService(db)
        user = auth_service.register_user(user_data)
        
        logger.info(f"Successfully registered user with ID: {user.user_id}")
        return user
        
    except CustomException as e:
        logger.error(f"Registration failed: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "E003", "message": "Internal server error"}
        )
```

#### User Login
```python
@router.post("/login", response_model=Token)
async def login_user(
    credentials: LoginCredentials,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token
    
    Args:
        credentials: User login credentials
        db: Database session
    
    Returns:
        Token: JWT token and user information
    """
    try:
        logger.info(f"Login attempt for email: {credentials.email}")
        
        auth_service = AuthService(db)
        token_data = auth_service.authenticate_user(credentials)
        
        logger.info(f"Successful login for user: {credentials.email}")
        return token_data
        
    except CustomException as e:
        logger.error(f"Login failed: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
```

### 2. File Upload Endpoints (`app/api/v1/files.py`)

#### File Upload and Processing
```python
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_user
from app.services.file_service import FileService
from app.schemas.file import FileUploadResponse, FileListResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    engagement_name: str = Form(...),
    date1: str = Form(...),
    date2: str = Form(...),
    date3: str = Form(...),
    date4: str = Form(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process a file
    
    Args:
        file: File to upload (XLSX or CSV)
        engagement_name: Name for the engagement
        date1-date4: Four required dates
        current_user: Authenticated user
        db: Database session
    
    Returns:
        FileUploadResponse: Upload confirmation and processing status
    """
    try:
        logger.info(f"File upload initiated by user {current_user.user_id}")
        
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.csv')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": "E001", "message": "Only XLSX and CSV files are allowed"}
            )
        
        # Validate file size (50MB limit)
        if file.size > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": "E002", "message": "File size exceeds 50MB limit"}
            )
        
        file_service = FileService(db)
        result = await file_service.process_file_upload(
            file=file,
            user_id=current_user.user_id,
            engagement_name=engagement_name,
            dates=[date1, date2, date3, date4]
        )
        
        logger.info(f"File upload completed successfully: {result.file_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "E003", "message": "File upload failed"}
        )
```

---

## Authentication & Security

### JWT Token Management (`app/core/security.py`)
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityManager:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"Token verification failed: {str(e)}")
            return None
```

### Dependency Injection (`app/api/deps.py`)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import SecurityManager
from app.models.user import User
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
    
    Returns:
        User: Authenticated user object
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        security_manager = SecurityManager()
        
        payload = security_manager.verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "E004", "message": "Invalid token"}
            )
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "E004", "message": "Invalid token payload"}
            )
        
        user = db.query(User).filter(User.user_id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "E004", "message": "User not found"}
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "E004", "message": "Authentication failed"}
        )
```

---

## File Processing Workflow

### File Service (`app/services/file_service.py`)
```python
import os
import shutil
import pandas as pd
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.file import File
from app.models.user import User
from app.utils.file_utils import FileUtils
from app.services.processing_service import ProcessingService
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.file_utils = FileUtils()
        self.processing_service = ProcessingService()
    
    async def process_file_upload(
        self,
        file,
        user_id: int,
        engagement_name: str,
        dates: List[str]
    ):
        """
        Process file upload workflow
        
        Args:
            file: Uploaded file
            user_id: User ID
            engagement_name: Engagement name
            dates: List of 4 dates
        
        Returns:
            FileUploadResponse: Processing result
        """
        try:
            # Step 1: Store file in input directory
            input_path = await self._store_input_file(file, user_id)
            
            # Step 2: Create database record
            file_record = self._create_file_record(
                user_id=user_id,
                filename=file.filename,
                input_path=input_path,
                engagement_name=engagement_name,
                dates=dates
            )
            
            # Step 3: Process file
            output_path = await self._process_file(input_path, user_id)
            
            # Step 4: Update database with results
            self._update_file_record(file_record, output_path)
            
            logger.info(f"File processing completed: {file_record.file_id}")
            return file_record
            
        except Exception as e:
            logger.error(f"File processing failed: {str(e)}")
            raise
    
    async def _store_input_file(self, file, user_id: int) -> str:
        """Store uploaded file in input directory"""
        try:
            # Create directory structure
            date_str = datetime.now().strftime("%Y-%m-%d")
            input_dir = f"/opt/landrover/{user_id}/{date_str}/input"
            os.makedirs(input_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(input_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File stored at: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"File storage failed: {str(e)}")
            raise
    
    def _create_file_record(
        self,
        user_id: int,
        filename: str,
        input_path: str,
        engagement_name: str,
        dates: List[str]
    ) -> File:
        """Create file record in database"""
        try:
            # Count lines in file (excluding header)
            line_count = self.file_utils.count_lines(input_path)
            
            file_record = File(
                user_id=user_id,
                upload_date=datetime.now().date(),
                filename=filename,
                original_filename=filename,
                line_count=line_count,
                storage_location=input_path,
                processed_flag=False,
                engagement_name=engagement_name
            )
            
            self.db.add(file_record)
            self.db.commit()
            self.db.refresh(file_record)
            
            logger.info(f"File record created: {file_record.file_id}")
            return file_record
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database record creation failed: {str(e)}")
            raise
    
    async def _process_file(self, input_path: str, user_id: int) -> str:
        """Process file using core business logic"""
        try:
            # Create output directory
            date_str = datetime.now().strftime("%Y-%m-%d")
            output_dir = f"/opt/landrover/{user_id}/{date_str}/output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Process file
            output_filename = f"processed_{os.path.basename(input_path)}"
            output_path = os.path.join(output_dir, output_filename)
            
            await self.processing_service.process_file(input_path, output_path)
            
            logger.info(f"File processed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"File processing failed: {str(e)}")
            raise
    
    def _update_file_record(self, file_record: File, output_path: str):
        """Update file record with processing results"""
        try:
            file_record.processed_flag = True
            file_record.storage_location = output_path
            file_record.updated_at = datetime.now()
            
            self.db.commit()
            logger.info(f"File record updated: {file_record.file_id}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"File record update failed: {str(e)}")
            raise
```

---

## Error Handling

### Custom Exceptions (`app/core/exceptions.py`)
```python
class CustomException(Exception):
    def __init__(self, message: str, status_code: int, error_code: str):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class ValidationException(CustomException):
    def __init__(self, message: str):
        super().__init__(message, 400, "E007")

class AuthenticationException(CustomException):
    def __init__(self, message: str):
        super().__init__(message, 401, "E004")

class FileProcessingException(CustomException):
    def __init__(self, message: str):
        super().__init__(message, 500, "E005")
```

---

## Configuration Management

### Environment Configuration (`app/core/config.py`)
```python
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/geopulse"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # File Storage
    UPLOAD_DIR: str = "/opt/landrover"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Development Setup

### 1. Project Initialization
```bash
# Create virtual environment
python -m venv geopulse-env
source geopulse-env/bin/activate  # On Windows: geopulse-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 2. Requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pandas==2.1.4
openpyxl==3.1.2
pytest==7.4.3
httpx==0.25.2
python-dotenv==1.0.0
```

### 3. Database Setup
```bash
# Run database migrations
alembic upgrade head

# Create initial data (if needed)
python scripts/create_initial_data.py
```

### 4. Running the Application
```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Testing

### Test Configuration (`tests/conftest.py`)
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "postgresql://test_user:test_pass@localhost/test_geopulse"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
```

### Example Test (`tests/test_auth.py`)
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_register_user(client: TestClient):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Test Org",
            "user_name": "Test User",
            "contact_phone": "1234567890",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "user_id" in data

def test_login_user(client: TestClient):
    """Test user login"""
    # First register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Test Org",
            "user_name": "Test User",
            "contact_phone": "1234567890",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    
    # Then login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
```

---

## Next Steps for Developers

1. **Set up the development environment** - Install Python, PostgreSQL, and dependencies
2. **Configure the database** - Set up PostgreSQL and run migrations
3. **Implement authentication** - Start with user registration and login
4. **Build file upload functionality** - Implement file storage and processing
5. **Add API endpoints** - Create all required endpoints with proper validation
6. **Implement error handling** - Add comprehensive error handling and logging
7. **Write tests** - Create unit and integration tests for all functionality
8. **Add documentation** - Document all endpoints and workflows
9. **Optimize performance** - Implement caching and database optimization
10. **Deploy and monitor** - Deploy to production and set up monitoring

Remember to:
- Follow the project structure exactly as specified
- Use proper error handling and logging
- Write comprehensive tests for all functionality
- Validate all inputs using Pydantic schemas
- Implement proper security measures
- Use environment variables for configuration
- Follow FastAPI best practices
