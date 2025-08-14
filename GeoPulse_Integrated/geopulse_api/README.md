# GeoPulse API

A FastAPI-based user registration and management system with secure authentication, database integration, and comprehensive validation.

## Features

- **User Registration**: Secure user registration with organization details
- **User Authentication**: Simple email/password login with JWT tokens
- **Password Security**: Bcrypt password hashing with configurable salt rounds
- **Database Integration**: Async SQLAlchemy with PostgreSQL support
- **File Management**: JSON file storage alongside database records
- **Comprehensive Validation**: Pydantic schemas with custom validators
- **Health Monitoring**: Built-in health check endpoints
- **Request Logging**: Simple text file logging for requests and errors
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip or poetry for dependency management

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd geopulse-api
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Set up PostgreSQL database:
```bash
# Create database and user using setup_postgres.sql
psql -U postgres -f setup_postgres.sql
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
app/
├── core/                    # Shared core functionality
│   ├── app_factory.py       # FastAPI application factory
│   ├── database.py          # Database connection management
│   ├── exceptions.py        # Custom exception classes
│   ├── logger.py           # Logging configuration
│   └── middleware.py       # Middleware configuration
├── shared/                  # Shared utilities and models
│   ├── models/base.py       # User and File models
│   ├── schemas/response.py  # Standardized response schemas
│   └── utils/              # Security and validation utilities
├── modules/                 # Feature modules
│   ├── registration/        # User registration module
│   ├── login/              # User authentication module
│   └── upload/             # File upload and processing module
├── middleware/             # Custom middleware components
│   ├── logging_middleware.py
│   ├── rate_limiting_middleware.py
│   └── security_middleware.py
└── api/v1/                 # API routing
    ├── router.py           # Main API router
    └── health.py          # Health check endpoints
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (returns JWT token)

### File Management
- `POST /api/v1/files/upload` - Upload and process files (XLSX/CSV)
- `GET /api/v1/files/list` - List user's uploaded files
- `GET /api/v1/files/{id}/status` - Get file processing status

### Health & Monitoring
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system health
- `GET /middleware-info` - Middleware configuration info

## Configuration

Key environment variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://geopulse_user:password123@localhost:5432/geopulse_db

# Security
BCRYPT_ROUNDS=12
SECRET_KEY=your-secret-key-here

# File Storage
USER_JSON_DIR=./user_data
DEFAULT_LOGO_PATH=/defaults/datalegos.png

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/api.log
```

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Code Quality
The project follows Python best practices with:
- Type hints throughout
- Pydantic for data validation
- Async/await for database operations
- Dependency injection pattern
- Comprehensive error handling

## Architecture

### Layered Architecture
1. **API Layer** (`app/api/`): FastAPI endpoints and routing
2. **Service Layer** (`app/services/`): Business logic and orchestration
3. **Repository Layer** (`app/repositories/`): Data access abstraction
4. **Model Layer** (`app/models/`): Database models and schemas

### Key Components
- **UserService**: Handles user registration workflow
- **PasswordService**: Secure password hashing and validation
- **FileService**: JSON file management
- **UserRepository**: Database operations for users

## Security Features

- Bcrypt password hashing
- JWT token authentication (30-minute expiration)
- Input validation and sanitization
- SQL injection prevention via SQLAlchemy
- Directory traversal protection
- Password redaction in logs
- Request/response logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]