"""FastAPI application factory."""

from fastapi import FastAPI

from app.config import settings
from app.core.middleware import configure_middleware, get_middleware_info


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Configure all middleware using the centralized configuration
    configure_middleware(app)
    
    # Add a simple health check endpoint for testing
    @app.get("/")
    async def root():
        return {"message": "GeoPulse API is running", "status": "healthy"}
    
    # Add middleware info endpoint for debugging
    @app.get("/middleware-info")
    async def middleware_info():
        return get_middleware_info()
    
    # Include API routes
    from app.api.v1.router import api_router
    app.include_router(api_router, prefix="/api/v1")
    
    return app