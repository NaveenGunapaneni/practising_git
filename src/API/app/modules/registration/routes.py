"""Registration module API routes."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.core.database import get_db_session
from app.modules.registration.schemas import UserRegistrationRequest, UserRegistrationResponse, UserData
from app.modules.registration.services import RegistrationService
from app.modules.registration.repository import RegistrationRepository
from app.core.exceptions import ValidationException, DuplicateEmailException, DatabaseException, FileSystemException
from app.core.error_handler import ErrorHandler
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserRegistrationResponse, status_code=201)
async def register_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user in the GeoPulse system.
    
    This endpoint handles user registration with organization details,
    secure password hashing, and dual storage (database + JSON file).
    """
    try:
        # Parse request body manually to handle validation errors properly
        body = await request.json()
        
        # Validate the request data
        try:
            user_data = UserRegistrationRequest(**body)
        except ValidationError as e:
            # Convert Pydantic validation errors to our format
            error_details = []
            for error in e.errors():
                field = error['loc'][-1] if error['loc'] else 'unknown'
                message = error['msg']
                error_details.append({
                    "field": field,
                    "message": message
                })
            
            raise HTTPException(
                status_code=422,
                detail={
                    "status": "error",
                    "error_code": "E007",
                    "message": "Invalid input data",
                    "details": error_details,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Initialize services
        registration_repository = RegistrationRepository(db)
        registration_service = RegistrationService(repository=registration_repository)
        
        # Register the user
        user = await registration_service.register_user(user_data)
        
        # Create response data (excluding password_hash)
        user_response_data = UserData(
            user_id=user.user_id,
            organization_name=user.organization_name,
            user_name=user.user_name,
            contact_phone=user.contact_phone,
            email=user.email,
            logo_path=user.logo_path,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return UserRegistrationResponse(
            data=user_response_data,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except ValidationException as e:
        raise HTTPException(
            status_code=422,
            detail={
                "status": "error",
                "error_code": "E007",
                "message": e.message,
                "details": [{"field": e.field, "message": e.message}] if e.field else [],
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except DuplicateEmailException as e:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error_code": "E007",
                "message": "Validation failed: Email already exists",
                "details": {
                    "field": "email",
                    "value": e.email,
                    "constraint": "unique"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "E003",
                "message": "Database operation failed",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except FileSystemException as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "E006",
                "message": "File system operation failed",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "E003",
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat()
            }
        )