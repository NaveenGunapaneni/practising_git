# API-3: Dashboard Data - Technical Specification Document
## GeoPulse Web Application

**API Version:** 1.0  
**Date:** August 2025  
**Endpoint:** `/api/v1/dashboard`  
**Method:** GET  
**Authentication:** Required (JWT Bearer Token)  

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
Retrieve comprehensive dashboard data for authenticated users including file information, user details, and processing metrics.

### Business Rules
- Only authenticated users can access dashboard data
- Data is scoped to the authenticated user only
- File information includes upload history and processing status
- Metrics are calculated in real-time from database
- Dashboard data is cached for 5 minutes to improve performance

---

## Input Specification

### Request Headers
```
Authorization: Bearer <jwt_token>
Accept: application/json
Content-Type: application/json
```

### Query Parameters (Optional)
```
limit: integer (optional, default: 50, max: 100)
offset: integer (optional, default: 0)
sort_by: string (optional, values: "upload_date", "filename", "engagement_name", default: "upload_date")
sort_order: string (optional, values: "asc", "desc", default: "desc")
status: string (optional, values: "all", "processed", "pending", default: "all")
```

### Example Request
```
GET /api/v1/dashboard?limit=20&offset=0&sort_by=upload_date&sort_order=desc&status=processed
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Input Validation Rules
| Parameter | Type | Required | Default | Min | Max | Allowed Values |
|-----------|------|----------|---------|-----|-----|----------------|
| limit | integer | No | 50 | 1 | 100 | Any integer in range |
| offset | integer | No | 0 | 0 | 10000 | Any integer in range |
| sort_by | string | No | upload_date | - | - | upload_date, filename, engagement_name |
| sort_order | string | No | desc | - | - | asc, desc |
| status | string | No | all | - | - | all, processed, pending |

---

## Output Specification

### Success Response (HTTP 200 OK)
```json
{
    "status": "success",
    "data": {
        "user": {
            "user_id": 123,
            "user_name": "John Doe",
            "email": "john.doe@acmecorp.com",
            "organization_name": "Acme Corporation",
            "logo_path": "/uploads/logos/acme_logo.png",
            "created_at": "2025-01-15T10:30:00Z"
        },
        "files": [
            {
                "file_id": 456,
                "filename": "Q1_Financial_Data.xlsx",
                "original_filename": "Q1_Financial_Data.xlsx",
                "upload_date": "2025-08-01",
                "engagement_name": "Q1 Financial Analysis",
                "processed_flag": true,
                "line_count": 1250,
                "storage_location": "/opt/landrover/123/2025-08-01/output/processed_Q1_Financial_Data.xlsx",
                "created_at": "2025-08-01T10:30:00Z",
                "updated_at": "2025-08-01T10:35:00Z"
            },
            {
                "file_id": 457,
                "filename": "Q2_Data.csv",
                "original_filename": "Q2_Data.csv",
                "upload_date": "2025-07-25",
                "engagement_name": "Q2 Quarterly Review",
                "processed_flag": false,
                "line_count": 890,
                "storage_location": "/opt/landrover/123/2025-07-25/input/Q2_Data.csv",
                "created_at": "2025-07-25T14:20:00Z",
                "updated_at": "2025-07-25T14:20:00Z"
            }
        ],
        "metrics": {
            "total_files": 15,
            "processed_files": 12,
            "pending_files": 3,
            "total_lines": 18500,
            "average_lines_per_file": 1233,
            "files_this_month": 5,
            "files_this_week": 2,
            "storage_used_mb": 45.2
        },
        "pagination": {
            "current_page": 1,
            "total_pages": 3,
            "total_items": 15,
            "items_per_page": 20,
            "has_next": true,
            "has_previous": false
        }
    },
    "message": "Dashboard data retrieved successfully",
    "timestamp": "2025-08-01T10:30:00Z"
}
```

### Error Response (HTTP 401 Unauthorized)
```json
{
    "status": "error",
    "error_code": "E004",
    "message": "Invalid or expired token",
    "timestamp": "2025-08-01T10:30:00Z"
}
```

### Error Response (HTTP 422 Unprocessable Entity)
```json
{
    "status": "error",
    "error_code": "E007",
    "message": "Invalid query parameters",
    "details": [
        {
            "field": "limit",
            "message": "Limit must be between 1 and 100"
        },
        {
            "field": "sort_by",
            "message": "Invalid sort field"
        }
    ],
    "timestamp": "2025-08-01T10:30:00Z"
}
```

### Error Response (HTTP 500 Internal Server Error)
```json
{
    "status": "error",
    "error_code": "E003",
    "message": "Failed to retrieve dashboard data",
    "timestamp": "2025-08-01T10:30:00Z"
}
```

---

## Processing Logic

### Step-by-Step Processing
1. **Authentication Validation**
   - Extract JWT token from Authorization header
   - Verify token signature and expiration
   - Decode token to get user_id
   - Validate user exists and is active

2. **Input Parameter Processing**
   - Parse and validate query parameters
   - Set default values for missing parameters
   - Sanitize input to prevent injection attacks
   - Apply parameter constraints and limits

3. **User Data Retrieval**
   - Query user information from database
   - Include user profile and organization details
   - Verify user permissions and access rights
   - Format user data for response

4. **File Data Retrieval**
   - Build dynamic SQL query based on parameters
   - Apply filtering by user_id and status
   - Implement pagination with limit and offset
   - Sort results according to sort_by and sort_order
   - Retrieve file metadata and processing status

5. **Metrics Calculation**
   - Calculate total files count for user
   - Count processed vs pending files
   - Sum total lines across all files
   - Calculate average lines per file
   - Count files uploaded this month and week
   - Calculate storage usage in MB

6. **Pagination Processing**
   - Calculate total pages based on total items
   - Determine current page from offset
   - Set has_next and has_previous flags
   - Apply pagination to file results

7. **Response Assembly**
   - Combine user, files, metrics, and pagination data
   - Format timestamps in ISO 8601 format
   - Exclude sensitive information
   - Apply response caching for 5 minutes

8. **Performance Optimization**
   - Use database indexes for efficient queries
   - Implement query result caching
   - Optimize metrics calculation with aggregation
   - Minimize database round trips

---

## Database Operations

### Database Connection
- **Database:** PostgreSQL 15+
- **Connection String:** `postgresql://geopulse_user:password123@localhost:5432/geopulse_db`
- **Connection Pool:** 20-50 connections
- **Transaction:** Read-only transaction for data retrieval

### SQL Operations
```sql
-- Get user information
SELECT 
    user_id, 
    user_name, 
    email, 
    organization_name, 
    logo_path, 
    created_at
FROM users 
WHERE user_id = $1;

-- Get files with pagination and filtering
SELECT 
    file_id,
    filename,
    original_filename,
    upload_date,
    engagement_name,
    processed_flag,
    line_count,
    storage_location,
    created_at,
    updated_at
FROM files 
WHERE user_id = $1
  AND ($2 = 'all' OR 
       ($2 = 'processed' AND processed_flag = true) OR 
       ($2 = 'pending' AND processed_flag = false))
ORDER BY 
    CASE WHEN $3 = 'upload_date' THEN upload_date END DESC,
    CASE WHEN $3 = 'filename' THEN filename END ASC,
    CASE WHEN $3 = 'engagement_name' THEN engagement_name END ASC
LIMIT $4 OFFSET $5;

-- Get total count for pagination
SELECT COUNT(*) as total_count
FROM files 
WHERE user_id = $1
  AND ($2 = 'all' OR 
       ($2 = 'processed' AND processed_flag = true) OR 
       ($2 = 'pending' AND processed_flag = false));

-- Calculate metrics
SELECT 
    COUNT(*) as total_files,
    SUM(CASE WHEN processed_flag = true THEN 1 ELSE 0 END) as processed_files,
    SUM(CASE WHEN processed_flag = false THEN 1 ELSE 0 END) as pending_files,
    COALESCE(SUM(line_count), 0) as total_lines,
    COALESCE(AVG(line_count), 0) as average_lines_per_file,
    SUM(CASE WHEN upload_date >= DATE_TRUNC('month', CURRENT_DATE) THEN 1 ELSE 0 END) as files_this_month,
    SUM(CASE WHEN upload_date >= DATE_TRUNC('week', CURRENT_DATE) THEN 1 ELSE 0 END) as files_this_week
FROM files 
WHERE user_id = $1;
```

### Database Schema Details
```sql
-- Files table with indexes for dashboard queries
CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_upload_date ON files(upload_date);
CREATE INDEX idx_files_processed_flag ON files(processed_flag);
CREATE INDEX idx_files_user_processed ON files(user_id, processed_flag);
CREATE INDEX idx_files_user_date ON files(user_id, upload_date DESC);

-- Composite index for efficient dashboard queries
CREATE INDEX idx_dashboard_query ON files(user_id, processed_flag, upload_date DESC);
```

### Query Optimization
- **Index Usage:** Ensure all queries use appropriate indexes
- **Query Planning:** Use EXPLAIN ANALYZE to optimize queries
- **Connection Pooling:** Reuse database connections efficiently
- **Result Caching:** Cache frequently accessed data

---

## Security Requirements

### Authentication
- **JWT Token Validation:** Verify token signature and expiration
- **User Authorization:** Ensure user can only access their own data
- **Token Scope:** Validate token contains correct user_id
- **Session Management:** Track user sessions for security monitoring

### Data Protection
- **Row-Level Security:** Implement RLS policies in database
- **Data Isolation:** Ensure users cannot access other users' data
- **Input Sanitization:** Prevent SQL injection through parameterized queries
- **Output Filtering:** Remove sensitive data from responses

### Access Control
- **Rate Limiting:** Limit dashboard requests per user
- **Request Validation:** Validate all query parameters
- **Audit Logging:** Log all dashboard access attempts
- **Session Timeout:** Enforce session expiration

### Security Headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## Logging Requirements

### Log Levels and Messages
```python
# INFO Level
"Dashboard access for user_id: {user_id}"
"Dashboard data retrieved successfully for user: {user_id}"
"Dashboard metrics calculated for user: {user_id}"

# WARNING Level
"Slow dashboard query detected for user: {user_id}, duration: {duration}ms"
"Large result set returned for user: {user_id}, count: {count}"

# ERROR Level
"Database connection failed during dashboard retrieval"
"Failed to calculate metrics for user: {user_id}"
"Authentication failed for dashboard access"

# DEBUG Level
"Dashboard query parameters: {params}"
"Database query executed: {query}"
"Cache hit/miss for dashboard data"
```

### Log Format
```json
{
    "timestamp": "2025-08-01T10:30:00.123Z",
    "level": "INFO",
    "service": "dashboard_service",
    "operation": "get_dashboard_data",
    "user_id": 123,
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "query_params": {
        "limit": 20,
        "offset": 0,
        "sort_by": "upload_date",
        "status": "all"
    },
    "duration_ms": 245,
    "files_count": 15,
    "cache_hit": false
}
```

### Performance Logging
- **Query Execution Time:** Log slow queries (>500ms)
- **Result Set Size:** Log large result sets (>1000 items)
- **Cache Performance:** Track cache hit/miss ratios
- **Database Connection Usage:** Monitor connection pool utilization

---

## Exception Handling

### Custom Exceptions
```python
class DashboardAccessException(Exception):
    """Raised when user cannot access dashboard"""
    def __init__(self, message, user_id=None):
        self.message = message
        self.user_id = user_id
        self.error_code = "E004"

class MetricsCalculationException(Exception):
    """Raised when metrics calculation fails"""
    def __init__(self, message, user_id=None):
        self.message = message
        self.user_id = user_id
        self.error_code = "E003"

class PaginationException(Exception):
    """Raised when pagination parameters are invalid"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        self.error_code = "E007"
```

### Exception Response Mapping
| Exception Type | HTTP Status | Error Code | Response Format |
|----------------|-------------|------------|-----------------|
| DashboardAccessException | 401 | E004 | Authentication error |
| MetricsCalculationException | 500 | E003 | Server error |
| PaginationException | 422 | E007 | Validation error |
| DatabaseException | 500 | E003 | Database error |
| General Exception | 500 | E003 | Generic error |

### Error Response Structure
```json
{
    "status": "error",
    "error_code": "E003",
    "message": "Failed to retrieve dashboard data",
    "details": {
        "operation": "metrics_calculation",
        "user_id": 123
    },
    "timestamp": "2025-08-01T10:30:00Z",
    "request_id": "req_123456789"
}
```

---

## Performance Requirements

### Response Time Targets
- **P50 (Median):** < 300ms
- **P95 (95th percentile):** < 800ms
- **P99 (99th percentile):** < 1.5s
- **Timeout:** 10 seconds

### Throughput Requirements
- **Concurrent Users:** 100
- **Requests per Second:** 50
- **Database Queries:** Maximum 4 queries per request

### Resource Usage
- **Memory:** < 100MB per request
- **CPU:** < 15% per request
- **Database Connections:** Efficient connection pooling

### Caching Strategy
- **Dashboard Data:** Cache for 5 minutes per user
- **User Information:** Cache for 10 minutes
- **Metrics:** Cache for 2 minutes
- **File List:** Cache for 1 minute

### Optimization Techniques
- **Database Indexing:** Optimize indexes for dashboard queries
- **Query Optimization:** Use efficient SQL queries
- **Connection Pooling:** Reuse database connections
- **Result Caching:** Cache frequently accessed data
- **Pagination:** Implement efficient pagination

---

## Testing Instructions

### Postman Setup

#### 1. Create New Request
- **Method:** GET
- **URL:** `http://localhost:8000/api/v1/dashboard`
- **Headers:**
  ```
  Authorization: Bearer <your_jwt_token>
  Accept: application/json
  ```

#### 2. Query Parameters (Optional)
```
limit: 20
offset: 0
sort_by: upload_date
sort_order: desc
status: all
```

#### 3. Test Cases

**Test Case 1: Successful Dashboard Access**
- **Description:** Access dashboard with valid token
- **Expected Status:** 200 OK
- **Expected Response:** Complete dashboard data
- **Validation:**
  - Check user information is included
  - Verify files list is returned
  - Confirm metrics are calculated
  - Check pagination information

**Test Case 2: Unauthorized Access**
- **Description:** Access dashboard without token
- **Expected Status:** 401 Unauthorized
- **Expected Response:** Authentication error
- **Steps:**
  1. Remove Authorization header
  2. Send request
  3. Verify error response

**Test Case 3: Invalid Token**
- **Description:** Access dashboard with invalid token
- **Expected Status:** 401 Unauthorized
- **Expected Response:** Token validation error
- **Test Data:** `Authorization: Bearer invalid_token`

**Test Case 4: Pagination Test**
- **Description:** Test pagination functionality
- **Expected Status:** 200 OK
- **Test Data:** `limit=5&offset=10`
- **Validation:**
  - Check pagination metadata
  - Verify correct number of items returned
  - Confirm offset is applied correctly

**Test Case 5: Filtering by Status**
- **Description:** Filter files by processing status
- **Expected Status:** 200 OK
- **Test Data:** `status=processed`
- **Validation:**
  - Check only processed files are returned
  - Verify metrics reflect filtered data

**Test Case 6: Sorting Test**
- **Description:** Test different sorting options
- **Expected Status:** 200 OK
- **Test Data:** `sort_by=filename&sort_order=asc`
- **Validation:**
  - Check files are sorted by filename ascending
  - Verify sort order is applied correctly

**Test Case 7: Invalid Parameters**
- **Description:** Test with invalid query parameters
- **Expected Status:** 422 Unprocessable Entity
- **Test Data:** `limit=1000&sort_by=invalid_field`
- **Expected Response:** Validation error details

#### 4. Environment Variables
```json
{
    "base_url": "http://localhost:8000",
    "auth_token": "your_jwt_token_here",
    "test_user_id": 123
}
```

#### 5. Pre-request Script
```javascript
// Set authorization header
pm.request.headers.add({
    key: 'Authorization',
    value: 'Bearer ' + pm.environment.get('auth_token')
});
```

#### 6. Tests Script
```javascript
// Test successful response
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has user data", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.user).to.have.property('user_id');
    pm.expect(jsonData.data.user).to.have.property('user_name');
    pm.expect(jsonData.data.user).to.have.property('email');
});

pm.test("Response has files array", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.files).to.be.an('array');
});

pm.test("Response has metrics", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.metrics).to.have.property('total_files');
    pm.expect(jsonData.data.metrics).to.have.property('processed_files');
    pm.expect(jsonData.data.metrics).to.have.property('pending_files');
});

pm.test("Response has pagination", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.pagination).to.have.property('current_page');
    pm.expect(jsonData.data.pagination).to.have.property('total_pages');
    pm.expect(jsonData.data.pagination).to.have.property('total_items');
});

pm.test("Response structure is correct", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
    pm.expect(jsonData).to.have.property('data');
    pm.expect(jsonData).to.have.property('message');
    pm.expect(jsonData).to.have.property('timestamp');
});

// Performance test
pm.test("Response time is acceptable", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});
```

### Automated Testing

#### Unit Test Example
```python
def test_dashboard_access_success(client, auth_token):
    """Test successful dashboard access"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = client.get("/api/v1/dashboard", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["user"]["user_id"] is not None
    assert isinstance(data["data"]["files"], list)
    assert data["data"]["metrics"]["total_files"] >= 0

def test_dashboard_unauthorized(client):
    """Test dashboard access without token"""
    response = client.get("/api/v1/dashboard")
    
    assert response.status_code == 401
    data = response.json()
    assert "Invalid or expired token" in data["message"]

def test_dashboard_pagination(client, auth_token):
    """Test dashboard pagination"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = client.get("/api/v1/dashboard?limit=5&offset=0", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]["files"]) <= 5
    assert data["data"]["pagination"]["items_per_page"] == 5
```

#### Integration Test Example
```python
def test_dashboard_filtering(client, auth_token):
    """Test dashboard filtering by status"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test processed files filter
    response = client.get("/api/v1/dashboard?status=processed", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all returned files are processed
    for file in data["data"]["files"]:
        assert file["processed_flag"] == True
```

---

## Monitoring and Alerts

### Key Metrics to Monitor
- **Response Time:** P95 < 800ms
- **Success Rate:** > 98%
- **Cache Hit Rate:** > 80%
- **Database Query Performance:** < 500ms average

### Alert Conditions
- **Slow Response Time:** P95 > 1s for 5 minutes
- **High Error Rate:** > 5% errors in 5 minutes
- **Cache Miss Rate:** < 70% for 10 minutes
- **Database Connection Issues:** Connection pool exhaustion

### Performance Monitoring
- **Query Execution Time:** Monitor slow queries
- **Memory Usage:** Track memory consumption
- **CPU Usage:** Monitor CPU utilization
- **Database Connections:** Track connection pool usage

---

## Deployment Considerations

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://geopulse_user:password123@localhost:5432/geopulse_db

# Caching
REDIS_URL=redis://localhost:6379
CACHE_TTL_SECONDS=300

# Performance
MAX_DASHBOARD_ITEMS=100
DASHBOARD_CACHE_TTL=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/geopulse/dashboard.log
```

### Dependencies
- PostgreSQL 15+
- Python 3.11+
- FastAPI 0.104+
- Redis 6.0+ (for caching)
- SQLAlchemy 2.0+
- PyJWT 2.8+

### Health Checks
- Database connectivity
- Cache connectivity
- Response time monitoring
- Memory and CPU usage
- Error rate monitoring
