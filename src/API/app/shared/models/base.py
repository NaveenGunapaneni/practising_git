"""Base model classes and shared database models."""

from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """User model for storing user registration data."""
    
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    organization_name = Column(String(255), nullable=False, index=True)
    user_name = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    logo_path = Column(String(500), default="/defaults/datalegos.png")
    file_count = Column(Integer, default=0, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationship
    files = relationship("File", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email='{self.email}')>"
    
    def to_dict(self) -> dict:
        """Convert user model to dictionary, excluding password_hash."""
        return {
            "user_id": self.user_id,
            "organization_name": self.organization_name,
            "user_name": self.user_name,
            "contact_phone": self.contact_phone,
            "email": self.email,
            "logo_path": self.logo_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class File(Base):
    """File model for storing file upload and processing data."""
    
    __tablename__ = "files"
    
    file_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    upload_date = Column(Date, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    line_count = Column(Integer)
    storage_location = Column(String(500), nullable=False)
    input_location = Column(String(500))
    processed_flag = Column(Boolean, default=False, nullable=False, index=True)
    engagement_name = Column(String(255))
    browser_ip = Column(String(45))
    browser_location = Column(String(255))
    processing_time_seconds = Column(Numeric(10, 2))
    file_size_mb = Column(Numeric(10, 2))
    dates = Column(JSONB)  # Store the 4 dates as JSON array
    error_message = Column(Text)
    created_at = Column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationship
    user = relationship("User", back_populates="files")
    
    def __repr__(self) -> str:
        return f"<File(file_id={self.file_id}, filename='{self.filename}', user_id={self.user_id})>"
    
    def to_dict(self) -> dict:
        """Convert file model to dictionary."""
        return {
            "file_id": self.file_id,
            "user_id": self.user_id,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "line_count": self.line_count,
            "storage_location": self.storage_location,
            "input_location": self.input_location,
            "processed_flag": self.processed_flag,
            "engagement_name": self.engagement_name,
            "browser_ip": self.browser_ip,
            "browser_location": self.browser_location,
            "processing_time_seconds": float(self.processing_time_seconds) if self.processing_time_seconds else None,
            "file_size_mb": float(self.file_size_mb) if self.file_size_mb else None,
            "dates": self.dates,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }