"""Login module API routes."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from app.core.database import get_db_session
from app.modules.login.schemas import LoginRequest, LoginResponse
from app.modules.login.services import LoginService
from app.modules.login.repository import LoginRepository
from app.core.exceptions import ValidationException, AuthenticationException, DatabaseException
from app.core.error_handler import ErrorHandler
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


async def get_login_credentials(
    request: Request,
    username: str = Form(None),
    password: str = Form(None)
) -> LoginRequest:
    """Extract login credentials from either form data or JSON."""
    # Check if form data was provided
    if username and password:
        return LoginRequest(username=username, password=password)
    
    # Try to parse JSON data
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            body = await request.json()
            return LoginRequest(**body)
        elif "application/x-www-form-urlencoded" in content_type:
            # Handle form data manually if FastAPI didn't parse it
            form = await request.form()
            return LoginRequest(
                username=form.get("username"),
                password=form.get("password")
            )
    except Exception:
        pass
    
    raise ValidationException("Invalid request format or missing credentials")


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    username: str = Form(None),
    password: str = Form(None)
):
    """
    Authenticate user and return JWT access token.
    
    Accepts both JSON and form-encoded data:
    
    **JSON format:**
    ```json
    {
        "username": "john.doe@acme.com",
        "password": "securePassword123"
    }
    ```
    
    **Form data format:**
    ```
    username=john.doe@acme.com&password=securePassword123
    ```
    """
    try:
        # Get credentials from either form or JSON
        credentials = await get_login_credentials(request, username, password)
        
        # Initialize services
        login_repository = LoginRepository(db)
        login_service = LoginService(repository=login_repository)
        
        # Get client information
        client_ip, user_agent = login_service.get_client_info(request)
        
        # Authenticate user
        response = await login_service.authenticate_user(credentials, client_ip, user_agent)
        
        return response
        
    except AuthenticationException as e:
        raise HTTPException(
            status_code=401, 
            detail={
                "status": "error",
                "error_code": "E004",
                "message": "Invalid credentials",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except ValidationException as e:
        raise HTTPException(
            status_code=422,
            detail={
                "status": "error",
                "error_code": "E007",
                "message": "Invalid input data",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in login endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "E003",
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat()
            }
        )