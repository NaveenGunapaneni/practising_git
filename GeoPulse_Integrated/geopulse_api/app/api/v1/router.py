"""Main API router that combines all module routers."""

from fastapi import APIRouter

from app.modules.registration.routes import router as registration_router
from app.modules.login.routes import router as login_router
from app.modules.upload.routes import router as upload_router
from app.modules.dashboard.routes import router as dashboard_router
from app.api.v1.health import router as health_router

# Create main API router
api_router = APIRouter()

# Include module routers
api_router.include_router(registration_router, prefix="/auth", tags=["registration"])
api_router.include_router(login_router, prefix="/auth", tags=["login"])
api_router.include_router(upload_router, prefix="/files", tags=["upload"])
api_router.include_router(dashboard_router, tags=["dashboard"])
api_router.include_router(health_router, tags=["health"])