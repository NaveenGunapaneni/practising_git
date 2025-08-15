# API-2: User Authentication - Technical Specification Document
## GeoPulse Web Application

**API Version:** 1.0  
**Date:** August 2025  
**Endpoint:** `/api/v1/auth/login`  
**Method:** POST  
**Content-Type:** application/x-www-form-urlencoded  

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
Authenticate user credentials and return JWT access token for subsequent API requests.

### Business Rules
- User must be registered before authentication
- Password verification using bcrypt hashing
- JWT token expires after 30 minutes
- Failed login attempts are logged for security monitoring
- User session information is tracked

---

## Input Specification

### Request Headers
```
Content-Type: application/x-www-form-urlencoded
Accept: application/json
```

### Request Body (Form Data)
```
username: string (required, valid email format)
password: string (required, min 6 chars)
```

### Input Validation Rules
| Field | Type | Required | Min Length | Max Length | Format/Pattern |
|-------|------|----------|------------|------------|----------------|
| username | string | Yes | 5 | 255 | Valid email format |
| password | string | Yes | 6 | 255 | Any printable characters |

### Example Valid Input
```
username=john.doe@acmecorp.com&password=SecurePass123!
```

### Alternative JSON Input (if supported)
```json
{
    "username": "john.doe@acmecorp.com",
    "password": "SecurePass123!"
}
```

---

## Output Specification

### Success Response (HTTP 200 OK)
```json
{
    "status": "success",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjEyMywiZXhwIjoxNzM1NjgwMDAwfQ.signature",
        "token_type": "bearer",
        "expires_in": 1800,
        "user": {
            "user_id": 123,
            "user_name": "John Doe",
            "email": "john.doe@acmecorp.com",
            "organization_name": "Acme Corporation",
            "logo_path": "/uploads/logos/acme_logo.png"
        }
    },
    "message": "Login successful",
    "timestamp": "2025-08-01T10:30:00Z"
}
```

### Error Response (HTTP 401 Unauthorized)
```json
{
    "status": "error",
    "error_code": "E004",
    "message": "Invalid credentials",
    "details": {
        "attempts_remaining": 4,
        "lockout_time": null
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
            "field": "username",
            "message": "Invalid email format"
        },
        {
            "field": "password",
            "message": "Password is required"
        }
    ],
    "timestamp": "2025-08-01T10:30:00Z"
}
```

### Error Response (HTTP 429 Too Many Requests)
```json
{
    "status": "error",
    "error_code": "E004",
    "message": "Too many login attempts. Please try again later.",
    "details": {
        "lockout_time": "2025-08-01T10:35:00Z",
        "attempts_remaining": 0
    },
    "timestamp": "2025-08-01T10:30:00Z"
}
```

---

## Processing Logic

### Step-by-Step Processing
1. **Input Validation**
   - Validate form data structure
   - Check email format for username field
   - Ensure password is provided and meets minimum length
   - Sanitize input to prevent injection attacks

2. **Rate Limiting Check**
   - Check if IP address is rate limited
   - Verify if account is temporarily locked
   - Allow maximum 5 failed attempts per 15 minutes

3. **User Lookup**
   - Query database for user by email address
   - Check if user account exists and is active
   - Retrieve user data and password hash

4. **Password Verification**
   - Use bcrypt to verify password against stored hash
   - Compare password with salt rounds of 12
   - Handle password verification failures

5. **JWT Token Generation**
   - Generate JWT token with user ID as subject
   - Set expiration time to 30 minutes from now
   - Include user role and permissions in token payload
   - Sign token with application secret key

6. **Session Management**
   - Update user's last login timestamp
   - Log successful authentication attempt
   - Track user session for analytics

7. **Response Generation**
   - Format success response with token and user data
   - Include token expiration information
   - Exclude sensitive data (password hash, etc.)

---

## Database Operations

### Database Connection
- **Database:** PostgreSQL 15+
- **Connection String:** `postgresql://geopulse_user:password123@localhost:5432/geopulse_db`
- **Connection Pool:** 20-50 connections
- **Transaction:** Required for user data updates

### SQL Operations
```sql
-- Find user by email
SELECT 
    user_id, 
    user_name, 
    email, 
    password_hash, 
    organization_name, 
    logo_path,
    last_login_at,
    failed_login_attempts,
    account_locked_until
FROM users 
WHERE email = $1 AND account_locked_until IS NULL OR account_locked_until < NOW();

-- Update last login time
UPDATE users 
SET last_login_at = NOW(), failed_login_attempts = 0 
WHERE user_id = $1;

-- Increment failed login attempts
UPDATE users 
SET failed_login_attempts = failed_login_attempts + 1,
    account_locked_until = CASE 
        WHEN failed_login_attempts >= 4 THEN NOW() + INTERVAL '15 minutes'
        ELSE account_locked_until 
    END
WHERE user_id = $1;
```

### Database Schema Details
```sql
-- Users table with authentication fields
ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN account_locked_until TIMESTAMP WITH TIME ZONE;

-- Indexes for authentication
CREATE INDEX idx_users_email_active ON users(email) WHERE account_locked_until IS NULL OR account_locked_until < NOW();
CREATE INDEX idx_users_last_login ON users(last_login_at);
```

---

## Security Requirements

### Password Security
- **Verification:** bcrypt with salt rounds of 12
- **Timing Attack Prevention:** Constant-time comparison
- **Password Storage:** Hashed passwords only, never plain text

### JWT Token Security
- **Algorithm:** HS256 (HMAC with SHA-256)
- **Secret Key:** 256-bit minimum, stored in environment variables
- **Token Expiration:** 30 minutes
- **Token Payload:**
  ```json
  {
    "sub": 123,
    "email": "john.doe@acmecorp.com",
    "role": "user",
    "iat": 1735680000,
    "exp": 1735681800
  }
  ```

### Rate Limiting
- **Failed Attempts:** Maximum 5 per 15 minutes per IP
- **Account Lockout:** 15 minutes after 5 failed attempts
- **IP-based Limiting:** 10 requests per minute per IP
- **Global Rate Limit:** 100 requests per minute

### Session Security
- **Token Storage:** Client-side only (localStorage/sessionStorage)
- **Token Transmission:** HTTPS only
- **Token Validation:** Verify signature and expiration on each request
- **Token Revocation:** Implement token blacklist for logout

---

## Logging Requirements

### Log Levels and Messages
```python
# INFO Level
"User login attempt for email: {email}"
"User login successful for user_id: {user_id}"
"JWT token generated for user: {user_id}"

# WARNING Level
"Failed login attempt for email: {email}"
"Account locked due to multiple failed attempts: {email}"
"Rate limit exceeded for IP: {ip_address}"

# ERROR Level
"Database connection failed during authentication"
"Password verification failed: {error}"
"JWT token generation failed: {error}"

# DEBUG Level
"Input validation passed for email: {email}"
"Password verification successful"
"User session updated"
```

### Log Format
```json
{
    "timestamp": "2025-08-01T10:30:00.123Z",
    "level": "INFO",
    "service": "auth_service",
    "operation": "authenticate_user",
    "user_id": 123,
    "email": "john.doe@acmecorp.com",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "success": true,
    "duration_ms": 156,
    "rate_limited": false
}
```

### Security Logging
- **Failed Login Attempts:** Log all failed attempts with IP and timestamp
- **Account Lockouts:** Log when accounts are locked/unlocked
- **Rate Limit Violations:** Log IP addresses that exceed rate limits
- **Suspicious Activity:** Log multiple failed attempts from same IP

---

## Exception Handling

### Custom Exceptions
```python
class AuthenticationException(Exception):
    """Raised when authentication fails"""
    def __init__(self, message, attempts_remaining=None, lockout_time=None):
        self.message = message
        self.attempts_remaining = attempts_remaining
        self.lockout_time = lockout_time
        self.error_code = "E004"

class RateLimitException(Exception):
    """Raised when rate limit is exceeded"""
    def __init__(self, message, lockout_time):
        self.message = message
        self.lockout_time = lockout_time
        self.error_code = "E004"

class UserNotFoundException(Exception):
    """Raised when user is not found"""
    def __init__(self, email):
        self.message = f"User not found: {email}"
        self.error_code = "E004"
```

### Exception Response Mapping
| Exception Type | HTTP Status | Error Code | Response Format |
|----------------|-------------|------------|-----------------|
| AuthenticationException | 401 | E004 | Invalid credentials |
| RateLimitException | 429 | E004 | Too many attempts |
| UserNotFoundException | 401 | E004 | Invalid credentials |
| ValidationException | 422 | E007 | Validation error details |
| DatabaseException | 500 | E003 | Database error message |

### Error Response Structure
```json
{
    "status": "error",
    "error_code": "E004",
    "message": "Invalid credentials",
    "details": {
        "attempts_remaining": 3,
        "lockout_time": null
    },
    "timestamp": "2025-08-01T10:30:00Z",
    "request_id": "req_123456789"
}
```

---

## Performance Requirements

### Response Time Targets
- **P50 (Median):** < 200ms
- **P95 (95th percentile):** < 500ms
- **P99 (99th percentile):** < 1s
- **Timeout:** 5 seconds

### Throughput Requirements
- **Concurrent Users:** 200
- **Requests per Second:** 100
- **Database Queries:** Maximum 2 queries per request

### Resource Usage
- **Memory:** < 50MB per request
- **CPU:** < 5% per request
- **Database Connections:** Efficient connection pooling

### Caching Strategy
- **User Data:** Cache for 5 minutes after successful login
- **Rate Limit Data:** Cache for 15 minutes
- **JWT Token Validation:** No caching (validate each time)

---

## Testing Instructions

### Postman Setup

#### 1. Create New Request
- **Method:** POST
- **URL:** `http://localhost:8000/api/v1/auth/login`
- **Headers:**
  ```
  Content-Type: application/x-www-form-urlencoded
  Accept: application/json
  ```

#### 2. Request Body (Form Data)
```
username: john.doe@acmecorp.com
password: SecurePass123!
```

#### 3. Test Cases

**Test Case 1: Successful Login**
- **Description:** Login with valid credentials
- **Expected Status:** 200 OK
- **Expected Response:** JWT token and user data
- **Validation:**
  - Check access_token is returned
  - Verify token_type is "bearer"
  - Confirm user data is included
  - Check expires_in is 1800 seconds

**Test Case 2: Invalid Password**
- **Description:** Login with wrong password
- **Expected Status:** 401 Unauthorized
- **Expected Response:** "Invalid credentials" error
- **Steps:**
  1. Use correct email with wrong password
  2. Verify attempts_remaining decreases

**Test Case 3: Non-existent User**
- **Description:** Login with unregistered email
- **Expected Status:** 401 Unauthorized
- **Expected Response:** "Invalid credentials" error
- **Test Data:** `username: nonexistent@example.com`

**Test Case 4: Account Lockout**
- **Description:** Login after multiple failed attempts
- **Expected Status:** 429 Too Many Requests
- **Expected Response:** Account locked message
- **Steps:**
  1. Make 5 failed login attempts
  2. Try 6th attempt
  3. Verify lockout message

**Test Case 5: Invalid Email Format**
- **Description:** Login with invalid email format
- **Expected Status:** 422 Unprocessable Entity
- **Test Data:** `username: invalid-email`
- **Expected Response:** Validation error for email field

**Test Case 6: Missing Password**
- **Description:** Login without password
- **Expected Status:** 422 Unprocessable Entity
- **Test Data:** Only provide username
- **Expected Response:** Validation error for password

#### 4. Environment Variables
```json
{
    "base_url": "http://localhost:8000",
    "valid_email": "john.doe@acmecorp.com",
    "valid_password": "SecurePass123!",
    "invalid_password": "WrongPassword123!"
}
```

#### 5. Pre-request Script
```javascript
// Set up test data
pm.environment.set("test_email", pm.environment.get("valid_email"));
pm.environment.set("test_password", pm.environment.get("valid_password"));
```

#### 6. Tests Script
```javascript
// Test successful login
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has access token", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.access_token).to.be.a('string');
    pm.expect(jsonData.data.access_token.length).to.be.greaterThan(100);
});

pm.test("Token type is bearer", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.token_type).to.eql('bearer');
});

pm.test("Token expires in 30 minutes", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.expires_in).to.eql(1800);
});

pm.test("User data is included", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.user).to.have.property('user_id');
    pm.expect(jsonData.data.user).to.have.property('email');
    pm.expect(jsonData.data.user.email).to.eql(pm.environment.get("test_email"));
});

pm.test("Response structure is correct", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
    pm.expect(jsonData).to.have.property('data');
    pm.expect(jsonData).to.have.property('message');
    pm.expect(jsonData).to.have.property('timestamp');
});

// Store token for other requests
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("auth_token", jsonData.data.access_token);
}
```

### Automated Testing

#### Unit Test Example
```python
def test_login_success(client, test_user):
    """Test successful user login"""
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["access_token"] is not None
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["expires_in"] == 1800
    assert data["data"]["user"]["email"] == test_user["email"]

def test_login_invalid_password(client, test_user):
    """Test login with invalid password"""
    login_data = {
        "username": test_user["email"],
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 401
    data = response.json()
    assert "Invalid credentials" in data["message"]
    assert data["details"]["attempts_remaining"] == 4

def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "somepassword"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 401
    data = response.json()
    assert "Invalid credentials" in data["message"]
```

#### Integration Test Example
```python
def test_account_lockout_after_failed_attempts(client, test_user):
    """Test account lockout after multiple failed attempts"""
    login_data = {
        "username": test_user["email"],
        "password": "wrongpassword"
    }
    
    # Make 5 failed attempts
    for i in range(5):
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
    
    # 6th attempt should be locked
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 429
    data = response.json()
    assert "Too many login attempts" in data["message"]
```

---

## Monitoring and Alerts

### Key Metrics to Monitor
- **Success Rate:** > 95%
- **Response Time:** P95 < 500ms
- **Failed Login Rate:** < 10%
- **Account Lockouts:** Track frequency and patterns

### Alert Conditions
- **High Failed Login Rate:** > 20% in 5 minutes
- **Multiple Account Lockouts:** > 10 lockouts in 10 minutes
- **Slow Response Time:** P95 > 1s for 5 minutes
- **JWT Token Generation Failures:** Any failures

### Security Monitoring
- **Failed Login Patterns:** Monitor for brute force attempts
- **IP-based Attacks:** Track failed attempts by IP address
- **Account Takeover Attempts:** Monitor for suspicious login patterns
- **Token Abuse:** Monitor for token reuse or manipulation

---

## Deployment Considerations

### Environment Variables
```bash
# Security
SECRET_KEY=your-256-bit-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Rate Limiting
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
RATE_LIMIT_PER_IP=10
RATE_LIMIT_WINDOW_MINUTES=1

# Database
DATABASE_URL=postgresql://geopulse_user:password123@localhost:5432/geopulse_db

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/geopulse/auth.log
```

### Dependencies
- PostgreSQL 15+
- Python 3.11+
- FastAPI 0.104+
- PyJWT 2.8+
- bcrypt 4.0+
- pydantic 2.5+

### Security Checklist
- [ ] HTTPS enabled in production
- [ ] Strong secret key configured
- [ ] Rate limiting implemented
- [ ] Account lockout mechanism active
- [ ] Failed login monitoring enabled
- [ ] JWT token expiration set
- [ ] Input validation active
- [ ] SQL injection prevention
- [ ] XSS protection enabled
- [ ] Security headers configured
