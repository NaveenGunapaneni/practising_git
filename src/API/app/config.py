"""Centralized application configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralized application settings with environment variable support."""
    
    # Database settings
    database_url: str = Field(
        default="postgresql+asyncpg://geopulse_user:password123@localhost:5432/geopulse_db",
        description="Database connection URL"
    )
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(default=30, description="Database max overflow connections")
    
    # Core security settings
    secret_key: str = Field(default="your-secret-key-here", description="Application secret key")
    
    # JWT settings (used by login module)
    jwt_secret_key: str = Field(default="your-jwt-secret-key-here", description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(default=30, description="JWT token expiration in minutes")
    
    # Password settings (used by registration module)
    bcrypt_rounds: int = Field(default=12, description="Bcrypt salt rounds")
    
    # File system settings (used by registration and upload modules)
    user_json_dir: str = Field(default="./user_data", description="Directory for user JSON files")
    default_logo_path: str = Field(default="/defaults/datalegos.png", description="Default logo path")
    
    # File upload settings (used by upload module)
    upload_max_file_size_mb: int = Field(default=50, description="Maximum file size in MB")
    upload_dir: str = Field(default="./user_data/uploads", description="Upload directory")
    upload_temp_dir: str = Field(default="./user_data/temp", description="Temporary upload directory")
    
    # File validation settings
    MAX_FILE_SIZE_MB: int = Field(default=50, description="Maximum file size in MB")
    ALLOWED_FILE_TYPES: list = Field(default=[".xlsx", ".csv", ".xls"], description="Allowed file extensions")
    ALLOWED_MIME_TYPES: list = Field(default=[
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx
        "application/vnd.ms-excel",  # xls
        "text/csv",  # csv
        "application/csv"  # csv alternative
    ], description="Allowed MIME types")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="./logs/api.log", description="Log file path")
    
    # API settings
    api_title: str = Field(default="GeoPulse API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    api_description: str = Field(default="GeoPulse File Upload and Processing API", description="API description")
    
    # CORS settings
    cors_allow_origins: str = Field(default="*", description="CORS allowed origins (comma-separated)")
    cors_allow_credentials: bool = Field(default=True, description="CORS allow credentials")
    
    # Rate limiting settings
    rate_limit_enabled: bool = Field(default=False, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=60, description="Requests per minute")
    rate_limit_per_hour: int = Field(default=1000, description="Requests per hour")
    
    # Security settings
    security_headers_enabled: bool = Field(default=True, description="Enable security headers")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()