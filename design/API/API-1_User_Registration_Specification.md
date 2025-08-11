# API-1: User Registration - Technical Specification Document
## GeoPulse Web Application

**API Version:** 1.0  
**Date:** August 2025  
**Endpoint:** `/api/v1/auth/register`  
**Method:** POST  
**Content-Type:** application/json  

---

## Table of Contents
1. [API Overview](#api-overview)
2. [Input Specification](#input-specification)
3. [Output Specification](#output-specification)
4. [Processing Logic](#processing-logic)
5. [Database Operations](#database-operations)
6. [Security Requirements](#security-requirements)
7. [Logging Requirements](#logging-requirements)
8. [Exception Handling](#exception-handling)
9. [Performance Requirements](#performance-requirements)
10. [Testing Instructions](#testing-instructions)

---

## API Overview

### Purpose
Register a new user in the GeoPulse system with organization details, user information, and authentication credentials.

### Business Rules
- Each email address must be unique across the system
- User ID is automatically generated upon successful registration
- Password must be securely hashed before storage
- Organization logo is optional (defaults to "datalegos" logo)
- User details are stored in both database and JSON file

---

## Input Specification

### Request Headers
```
Content-Type: application/json
Accept: application/json
```

### Request Body (JSON)
```json
{
    "organization_name": "string (required, max 255 chars)",
    "user_name": "string (required, max 255 chars)",
    "contact_phone": "string (required, 10-20 chars, phone format)",
    "email": "string (required, valid email format, max 255 chars)",
    "password": "string (required, min 6 chars, max 255 chars)",
    "logo_path": "string (optional, max 500 chars, file path)"
}
```

### Input Validation Rules
| Field | Type | Required | Min Length | Max Length | Format/Pattern |
|-------|------|----------|------------|------------|----------------|
| organization_name | string | Yes | 1 | 255 | Alphanumeric, spaces, hyphens |
| user_name | string | Yes | 1 | 255 | Alphanumeric, spaces |
| contact_phone | string | Yes | 10 | 20 | Phone number format |
| email | string | Yes | 5 | 255 | Valid email format |
| password | string | Yes | 6 | 255 | Any printable characters |
| logo_path | string | No | 0 | 500 | Valid file path |

### Example Valid Input
```json
{
    "organization_name": "Acme Corporation",
    "user_name": "John Doe",
    "contact_phone": "+1-555-123-4567",
    "email": "john.doe@acmecorp.com",
    "password": "SecurePass123!",
    "logo_path": "/uploads/logos/acme_logo.png"
}
```

---

## Output Specification

### Success Response (HTTP 201 Created)
```json
{
    "status": "success",
    "data": {
        "user_id": 123,
        "organization_name": "Acme Corporation",
        "user_name": "John Doe",
        "contact_phone": "+1-555-123-4567",
        "email": "john.doe@acmecorp.com",
        "logo_path": "/uploads/logos/acme_logo.png",
        "created_at": "2025-08-01T10:30:00Z",
        "updated_at": "2025-08-01T10:30:00Z"
    },
    "message": "User registered successfully",
    "timestamp": "2025-08-01T10:30:00Z"
}
```

### Error Response (HTTP 400 Bad Request)
```json
{
    "status": "error",
    "error_code": "E007",
    "message": "Validation failed: Email already exists",
    "details": {
        "field": "email",
        "value": "john.doe@acmecorp.com",
        "constraint": "unique"
    },
    "timestamp": "2025-08-01T10:30:00Z"
}
```

### Error Response (HTTP 422 Unprocessable Entity)
```json
{
    "status": "error",
    "error_code": "E007",
    "message": "Invalid input data",
    "details": [
        {
            "field": "email",
            "message": "Invalid email format"
        },
        {
            "field": "password",
            "message": "Password must be at least 6 characters"
        }
    ],
    "timestamp": "2025-08-01T10:30:00Z"
}
```

---

## Processing Logic

### Step-by-Step Processing
1. **Input Validation**
   - Validate JSON structure and required fields
   - Check email format using regex pattern
   - Validate phone number format
   - Check password strength (minimum 6 characters)
   - Validate organization name and user name (non-empty)

2. **Business Logic Validation**
   - Check if email already exists in database
   - Validate logo file path (if provided)
   - Generate unique user ID

3. **Data Processing**
   - Hash password using bcrypt with salt rounds of 12
   - Set default logo path if not provided: "/defaults/datalegos.png"
   - Generate current timestamp for created_at and updated_at

4. **Database Operations**
   - Insert new user record into users table
   - Commit transaction
   - Retrieve created user data with generated user_id

5. **File Operations**
   - Create JSON file with user details at: `/opt/users/{user_name}.json`
   - JSON file structure:
     ```json
     {
         "user_id": 123,
         "organization_name": "Acme Corporation",
         "user_name": "John Doe",
         "contact_phone": "+1-555-123-4567",
         "email": "john.doe@acmecorp.com",
         "logo_path": "/uploads/logos/acme_logo.png",
         "created_at": "2025-08-01T10:30:00Z"
     }
     ```

6. **Response Generation**
   - Format success response with user data
   - Exclude password_hash from response
   - Include appropriate HTTP status code (201)

---

## Database Operations

### Database Connection
- **Database:** PostgreSQL 15+
- **Connection String:** `postgresql://geopulse_user:password123@localhost:5432/geopulse_db`
- **Connection Pool:** 20-50 connections
- **Transaction:** Required (auto-commit disabled)

### SQL Operations
```sql
-- Check if email exists
SELECT user_id FROM users WHERE email = $1;

-- Insert new user
INSERT INTO users (
    organization_name, 
    user_name, 
    contact_phone, 
    email, 
    password_hash, 
    logo_path, 
    created_at, 
    updated_at
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
RETURNING user_id, organization_name, user_name, contact_phone, email, logo_path, created_at, updated_at;
```

### Database Schema Details
```sql
-- Users table structure
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    organization_name VARCHAR(255) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    logo_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_organization ON users(organization_name);
```

---

## Security Requirements

### Password Security
- **Hashing Algorithm:** bcrypt
- **Salt Rounds:** 12
- **Password Storage:** Never store plain text passwords
- **Password Validation:** Minimum 6 characters, no maximum limit

### Input Sanitization
- **SQL Injection Prevention:** Use parameterized queries
- **XSS Prevention:** Sanitize all string inputs
- **File Path Validation:** Validate logo_path to prevent directory traversal

### Data Protection
- **Sensitive Data:** Never return password_hash in response
- **Email Privacy:** Store email in encrypted format (optional enhancement)
- **Audit Trail:** Log all registration attempts (success/failure)

### Rate Limiting
- **Requests per IP:** 10 requests per minute
- **Burst Limit:** 20 requests per 5 minutes
- **Block Duration:** 15 minutes for excessive requests

---

## Logging Requirements

### Log Levels and Messages
```python
# INFO Level
"User registration initiated for email: {email}"
"User registered successfully with ID: {user_id}"
"User JSON file created: {file_path}"

# WARNING Level
"Registration attempt with existing email: {email}"
"Invalid logo path provided: {logo_path}"

# ERROR Level
"Database connection failed during registration"
"File system error creating user JSON file: {error}"
"Password hashing failed: {error}"

# DEBUG Level
"Input validation passed for email: {email}"
"Database transaction committed successfully"
```

### Log Format
```json
{
    "timestamp": "2025-08-01T10:30:00.123Z",
    "level": "INFO",
    "service": "auth_service",
    "operation": "register_user",
    "user_id": 123,
    "email": "john.doe@acmecorp.com",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "message": "User registered successfully",
    "duration_ms": 245
}
```

### Log Storage
- **Location:** `/var/log/geopulse/api.log`
- **Rotation:** Daily with 30-day retention
- **Backup:** Compressed logs archived monthly

---

## Exception Handling

### Custom Exceptions
```python
class ValidationException(Exception):
    """Raised when input validation fails"""
    def __init__(self, message, field=None, value=None):
        self.message = message
        self.field = field
        self.value = value
        self.error_code = "E007"

class DuplicateEmailException(Exception):
    """Raised when email already exists"""
    def __init__(self, email):
        self.message = f"Email already exists: {email}"
        self.error_code = "E007"

class DatabaseException(Exception):
    """Raised when database operations fail"""
    def __init__(self, message):
        self.message = message
        self.error_code = "E003"
```

### Exception Response Mapping
| Exception Type | HTTP Status | Error Code | Response Format |
|----------------|-------------|------------|-----------------|
| ValidationException | 422 | E007 | Validation error details |
| DuplicateEmailException | 400 | E007 | Email already exists |
| DatabaseException | 500 | E003 | Database error message |
| FileSystemException | 500 | E006 | File system error |
| General Exception | 500 | E003 | Generic error message |

### Error Response Structure
```json
{
    "status": "error",
    "error_code": "E007",
    "message": "Validation failed",
    "details": [
        {
            "field": "email",
            "message": "Invalid email format",
            "value": "invalid-email"
        }
    ],
    "timestamp": "2025-08-01T10:30:00Z",
    "request_id": "req_123456789"
}
```

---

## Performance Requirements

### Response Time Targets
- **P50 (Median):** < 500ms
- **P95 (95th percentile):** < 1.5s
- **P99 (99th percentile):** < 3s
- **Timeout:** 10 seconds

### Throughput Requirements
- **Concurrent Users:** 100
- **Requests per Second:** 50
- **Database Connections:** 20-50 pool size

### Resource Usage
- **Memory:** < 100MB per request
- **CPU:** < 10% per request
- **Database Queries:** Maximum 2 queries per request

### Caching Strategy
- **Email Existence Check:** Cache for 5 minutes
- **User Data:** No caching (always fresh data)

---

## Testing Instructions

### Postman Setup

#### 1. Create New Request
- **Method:** POST
- **URL:** `http://localhost:8000/api/v1/auth/register`
- **Headers:**
  ```
  Content-Type: application/json
  Accept: application/json
  ```

#### 2. Request Body (JSON)
```json
{
    "organization_name": "Test Corporation",
    "user_name": "John Doe",
    "contact_phone": "+1-555-123-4567",
    "email": "john.doe@testcorp.com",
    "password": "SecurePass123!",
    "logo_path": "/uploads/logos/test_logo.png"
}
```

#### 3. Test Cases

**Test Case 1: Successful Registration**
- **Description:** Register new user with valid data
- **Expected Status:** 201 Created
- **Expected Response:** User data with generated user_id
- **Validation:**
  - Check user_id is generated
  - Verify email is stored correctly
  - Confirm password is not returned
  - Check JSON file is created

**Test Case 2: Duplicate Email**
- **Description:** Register user with existing email
- **Expected Status:** 400 Bad Request
- **Expected Response:** "Email already exists" error
- **Steps:**
  1. Register first user
  2. Try to register second user with same email

**Test Case 3: Invalid Email Format**
- **Description:** Register with invalid email
- **Expected Status:** 422 Unprocessable Entity
- **Test Data:** `"email": "invalid-email"`
- **Expected Response:** Validation error for email field

**Test Case 4: Missing Required Fields**
- **Description:** Register without required fields
- **Expected Status:** 422 Unprocessable Entity
- **Test Data:** Remove "email" field
- **Expected Response:** Validation error for missing field

**Test Case 5: Weak Password**
- **Description:** Register with short password
- **Expected Status:** 422 Unprocessable Entity
- **Test Data:** `"password": "123"`
- **Expected Response:** Validation error for password length

#### 4. Environment Variables
```json
{
    "base_url": "http://localhost:8000",
    "test_email": "test@example.com",
    "test_password": "TestPass123!"
}
```

#### 5. Pre-request Script
```javascript
// Generate unique email for testing
pm.environment.set("unique_email", `test_${Date.now()}@example.com`);
```

#### 6. Tests Script
```javascript
// Test successful registration
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response has user_id", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.user_id).to.be.a('number');
});

pm.test("Email is stored correctly", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.email).to.eql(pm.environment.get("unique_email"));
});

pm.test("Password is not returned", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.password).to.be.undefined;
});

pm.test("Response structure is correct", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
    pm.expect(jsonData).to.have.property('data');
    pm.expect(jsonData).to.have.property('message');
    pm.expect(jsonData).to.have.property('timestamp');
});
```

### Automated Testing

#### Unit Test Example
```python
def test_register_user_success(client):
    """Test successful user registration"""
    user_data = {
        "organization_name": "Test Corp",
        "user_name": "John Doe",
        "contact_phone": "1234567890",
        "email": "john@testcorp.com",
        "password": "testpass123"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["email"] == user_data["email"]
    assert data["data"]["user_id"] is not None
    assert "password" not in data["data"]
```

#### Integration Test Example
```python
def test_register_user_duplicate_email(client):
    """Test registration with duplicate email"""
    user_data = {
        "organization_name": "Test Corp",
        "user_name": "John Doe",
        "contact_phone": "1234567890",
        "email": "john@testcorp.com",
        "password": "testpass123"
    }
    
    # First registration
    client.post("/api/v1/auth/register", json=user_data)
    
    # Second registration with same email
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 400
    data = response.json()
    assert "Email already exists" in data["message"]
```

---

## Monitoring and Alerts

### Key Metrics to Monitor
- **Success Rate:** > 95%
- **Response Time:** P95 < 1.5s
- **Error Rate:** < 5%
- **Database Connection Pool:** < 80% utilization

### Alert Conditions
- **High Error Rate:** > 10% errors in 5 minutes
- **Slow Response Time:** P95 > 2s for 5 minutes
- **Database Issues:** Connection pool exhaustion
- **File System Errors:** JSON file creation failures

### Health Check Endpoint
```
GET /health
Response: {"status": "healthy", "database": "connected", "timestamp": "2025-08-01T10:30:00Z"}
```

---

## Deployment Considerations

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://geopulse_user:password123@localhost:5432/geopulse_db

# Security
SECRET_KEY=your-secret-key-here
BCRYPT_ROUNDS=12

# File System
USER_JSON_DIR=/opt/users
DEFAULT_LOGO_PATH=/defaults/datalegos.png

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/geopulse/api.log
```

### Dependencies
- PostgreSQL 15+
- Python 3.11+
- FastAPI 0.104+
- SQLAlchemy 2.0+
- bcrypt 4.0+
- pydantic 2.5+

### Health Checks
- Database connectivity
- File system write permissions
- Memory and CPU usage
- Response time monitoring
