"""Health check endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session, check_database_connection
from app.config import settings
from pathlib import Path

router = APIRouter()


async def check_directory_access() -> bool:
    """Check if the user data directory is accessible for read/write operations."""
    try:
        user_data_dir = Path(settings.user_json_dir)
        # Ensure directory exists
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Test write access by creating a temporary file
        test_file = user_data_dir / ".access_test"
        test_file.write_text("test")
        test_file.unlink()
        
        return True
    except Exception:
        return False


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "geopulse-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db_session)):
    """Detailed health check with database and file system status."""
    
    # Check database connection
    db_healthy = await check_database_connection()
    
    # Check file system access
    fs_healthy = await check_directory_access()
    
    overall_status = "healthy" if db_healthy and fs_healthy else "unhealthy"
    
    return {
        "status": overall_status,
        "service": "geopulse-api",
        "checks": {
            "database": {
                "status": "connected" if db_healthy else "disconnected",
                "healthy": db_healthy
            },
            "file_system": {
                "status": "accessible" if fs_healthy else "inaccessible", 
                "healthy": fs_healthy
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }