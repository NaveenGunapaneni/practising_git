# API-4: File Upload Processing - Technical Specification Document
## GeoPulse Web Application

**API Version:** 1.0  
**Date:** August 2025  
**Endpoint:** `/api/v1/files/upload`  
**Method:** POST  
**Content-Type:** multipart/form-data  
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
Upload and process XLSX/CSV files with engagement details, store them in organized directory structure, and execute core business logic for data processing.

### Business Rules
- Only authenticated users can upload files
- Files must be XLSX or CSV format only
- Maximum file size is 50MB
- Files are stored in user-specific directories
- Processing includes core business logic execution
- Output files are generated with conditional formatting
- All file operations are logged for audit trail

---

## Input Specification

### Request Headers
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
Accept: application/json
```

### Request Body (Multipart Form Data)
```
file: File (required, XLSX or CSV, max 50MB)
engagement_name: string (required, max 255 chars)
date1: string (required, YYYY-MM-DD format)
date2: string (required, YYYY-MM-DD format)
date3: string (required, YYYY-MM-DD format)
date4: string (required, YYYY-MM-DD format)
```

### Input Validation Rules
| Field | Type | Required | Max Size | Format/Pattern | Validation |
|-------|------|----------|----------|----------------|------------|
| file | File | Yes | 50MB | .xlsx, .csv | File format and size |
| engagement_name | string | Yes | 255 chars | Alphanumeric, spaces | Non-empty string |
| date1 | string | Yes | 10 chars | YYYY-MM-DD | Valid date format |
| date2 | string | Yes | 10 chars | YYYY-MM-DD | Valid date format |
| date3 | string | Yes | 10 chars | YYYY-MM-DD | Valid date format |
| date4 | string | Yes | 10 chars | YYYY-MM-DD | Valid date format |

### Example Valid Input
```
POST /api/v1/files/upload
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

Content-Type: multipart/form-data

file: Q1_Financial_Data.xlsx (binary file content)
engagement_name: Q1 Financial Analysis
date1: 2025-01-15
date2: 2025-02-15
date3: 2025-03-15
date4: 2025-04-15
```

---

## Output Specification

### Success Response (HTTP 200 OK)
```json
{
    "status": "success",
    "data": {
        "file_id": 456,
        "filename": "Q1_Financial_Data.xlsx",
        "original_filename": "Q1_Financial_Data.xlsx",
        "engagement_name": "Q1 Financial Analysis",
        "upload_date": "2025-08-01",
        "processed_flag": true,
        "line_count": 1250,
        "storage_location": "/opt/landrover/123/2025-08-01/output/processed_Q1_Financial_Data.xlsx",
        "input_location": "/opt/landrover/123/2025-08-01/input/Q1_Financial_Data.xlsx",
        "processing_time_seconds": 45.2,
        "file_size_mb": 2.8,
        "dates": [
            "2025-01-15",
            "2025-02-15",
            "2025-03-15",
            "2025-04-15"
        ],
        "created_at": "2025-08-01T10:30:00Z",
        "updated_at": "2025-08-01T10:35:00Z"
    },
    "message": "File uploaded and processed successfully",
    "timestamp": "2025-08-01T10:35:00Z"
}
```

### Error Response (HTTP 400 Bad Request)
```json
{
    "status": "error",
    "error_code": "E001",
    "message": "Invalid file format. Only XLSX and CSV files are allowed.",
    "details": {
        "field": "file",
        "value": "document.pdf",
        "allowed_formats": ["xlsx", "csv"]
    },
    "timestamp": "2025-08-01T10:30:00Z"
}
```

### Error Response (HTTP 413 Payload Too Large)
```json
{
    "status": "error",
    "error_code": "E002",
    "message": "File size exceeds maximum limit of 50MB",
    "details": {
        "field": "file",
        "actual_size_mb": 75.2,
        "max_size_mb": 50
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
            "field": "engagement_name",
            "message": "Engagement name is required"
        },
        {
            "field": "date1",
            "message": "Invalid date format. Use YYYY-MM-DD"
        }
    ],
    "timestamp": "2025-08-01T10:30:00Z"
}
```

### Error Response (HTTP 500 Internal Server Error)
```json
{
    "status": "error",
    "error_code": "E005",
    "message": "File processing failed",
    "details": {
        "operation": "core_processing",
        "error": "Processing timeout after 300 seconds"
    },
    "timestamp": "2025-08-01T10:30:00Z"
}
```

---

## Processing Logic

### Step-by-Step Processing
1. **Authentication and Authorization**
   - Validate JWT token and extract user_id
   - Verify user exists and is active
   - Check user permissions for file upload

2. **Input Validation**
   - Validate file format (XLSX or CSV only)
   - Check file size (maximum 50MB)
   - Validate engagement name (non-empty, max 255 chars)
   - Validate all 4 dates (YYYY-MM-DD format)
   - Sanitize all input data

3. **File Storage Preparation**
   - Create directory structure: `/opt/landrover/{user_id}/{date}/input/`
   - Generate unique filename to prevent conflicts
   - Ensure directory permissions are correct
   - Reserve storage space

4. **File Upload and Storage**
   - Stream file content to temporary location
   - Validate file integrity (checksum verification)
   - Move file to final input location
   - Set appropriate file permissions
   - Log file storage operation

5. **Database Record Creation**
   - Create file record in database
   - Set initial processing status to false
   - Store file metadata and user information
   - Capture browser IP and location (if available)
   - Commit transaction

6. **Core Processing Execution**
   - Execute core business logic on input file
   - Process data according to business rules
   - Apply conditional formatting to output
   - Generate processed file in XLSX format
   - Store output in: `/opt/landrover/{user_id}/{date}/output/`

7. **Database Update**
   - Update file record with processing results
   - Set processed_flag to true
   - Update storage_location to output path
   - Record processing time and metrics
   - Commit final transaction

8. **Response Generation**
   - Format success response with file details
   - Include processing metrics and timing
   - Provide file access information
   - Log successful processing

### Core Business Logic (Plain English)
1. **Data Validation**: Check input file structure and data integrity
2. **Data Transformation**: Convert data formats and apply business rules
3. **Calculation Engine**: Perform mathematical operations and aggregations
4. **Inference Processing**: Apply machine learning or statistical analysis
5. **Formatting**: Apply conditional formatting based on business rules
6. **Output Generation**: Create final XLSX file with results
7. **Quality Assurance**: Verify output file integrity and completeness

---

## Database Operations

### Database Connection
- **Database:** PostgreSQL 15+
- **Connection String:** `postgresql://geopulse_user:password123@localhost:5432/geopulse_db`
- **Connection Pool:** 20-50 connections
- **Transaction:** Required for data consistency

### SQL Operations
```sql
-- Create file record
INSERT INTO files (
    user_id,
    upload_date,
    filename,
    original_filename,
    line_count,
    storage_location,
    processed_flag,
    engagement_name,
    browser_ip,
    browser_location,
    created_at,
    updated_at
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
RETURNING file_id, user_id, upload_date, filename, original_filename, 
          line_count, storage_location, processed_flag, engagement_name,
          created_at, updated_at;

-- Update file record after processing
UPDATE files 
SET processed_flag = true,
    storage_location = $1,
    line_count = $2,
    updated_at = NOW()
WHERE file_id = $3;

-- Get file processing status
SELECT 
    file_id,
    filename,
    processed_flag,
    storage_location,
    created_at,
    updated_at
FROM files 
WHERE file_id = $1 AND user_id = $2;
```

### Database Schema Details
```sql
-- Files table with processing fields
CREATE TABLE files (
    file_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    upload_date DATE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    line_count INTEGER,
    storage_location VARCHAR(500) NOT NULL,
    processed_flag BOOLEAN DEFAULT FALSE,
    engagement_name VARCHAR(255),
    browser_ip VARCHAR(45),
    browser_location VARCHAR(255),
    processing_time_seconds DECIMAL(10,2),
    file_size_mb DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for file processing
CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_processed_flag ON files(processed_flag);
CREATE INDEX idx_files_upload_date ON files(upload_date);
CREATE INDEX idx_files_user_processed ON files(user_id, processed_flag);
```

---

## Security Requirements

### File Upload Security
- **File Type Validation:** Strict MIME type checking
- **File Size Limits:** Maximum 50MB per file
- **Virus Scanning:** Scan uploaded files for malware
- **Content Validation:** Verify file structure and content
- **Path Traversal Prevention:** Validate file paths

### Authentication and Authorization
- **JWT Token Validation:** Verify token signature and expiration
- **User Authorization:** Ensure user can upload files
- **Rate Limiting:** Limit uploads per user (10 per hour)
- **Session Validation:** Verify active user session

### Data Protection
- **File Encryption:** Encrypt files at rest
- **Access Control:** Restrict file access to owner only
- **Audit Logging:** Log all file operations
- **Secure Storage:** Use secure file system permissions

### Input Sanitization
- **SQL Injection Prevention:** Use parameterized queries
- **XSS Prevention:** Sanitize all string inputs
- **File Path Validation:** Prevent directory traversal
- **Content Validation:** Validate file content structure

---

## Logging Requirements

### Log Levels and Messages
```python
# INFO Level
"File upload initiated for user_id: {user_id}, filename: {filename}"
"File stored successfully at: {storage_location}"
"File processing started for file_id: {file_id}"
"File processing completed for file_id: {file_id}"

# WARNING Level
"Large file uploaded: {filename}, size: {size_mb}MB"
"Slow processing detected for file_id: {file_id}, duration: {duration}s"
"File format validation warning: {filename}"

# ERROR Level
"File upload failed for user_id: {user_id}, error: {error}"
"File processing failed for file_id: {file_id}, error: {error}"
"Storage space insufficient for file: {filename}"
"Database transaction failed during file upload"

# DEBUG Level
"File validation passed: {filename}"
"Directory created: {directory_path}"
"Processing step completed: {step_name}"
"File checksum verified: {checksum}"
```

### Log Format
```json
{
    "timestamp": "2025-08-01T10:30:00.123Z",
    "level": "INFO",
    "service": "file_service",
    "operation": "upload_file",
    "user_id": 123,
    "file_id": 456,
    "filename": "Q1_Financial_Data.xlsx",
    "file_size_mb": 2.8,
    "processing_time_seconds": 45.2,
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "success": true,
    "duration_ms": 45200,
    "storage_location": "/opt/landrover/123/2025-08-01/output/processed_Q1_Financial_Data.xlsx"
}
```

### Security Logging
- **File Upload Attempts:** Log all upload attempts with details
- **Processing Failures:** Log processing errors with context
- **Access Violations:** Log unauthorized access attempts
- **System Errors:** Log system-level errors and exceptions

---

## Exception Handling

### Custom Exceptions
```python
class FileUploadException(Exception):
    """Raised when file upload fails"""
    def __init__(self, message, filename=None, user_id=None):
        self.message = message
        self.filename = filename
        self.user_id = user_id
        self.error_code = "E001"

class FileProcessingException(Exception):
    """Raised when file processing fails"""
    def __init__(self, message, file_id=None, operation=None):
        self.message = message
        self.file_id = file_id
        self.operation = operation
        self.error_code = "E005"

class StorageException(Exception):
    """Raised when storage operations fail"""
    def __init__(self, message, path=None):
        self.message = message
        self.path = path
        self.error_code = "E006"

class ValidationException(Exception):
    """Raised when input validation fails"""
    def __init__(self, message, field=None, value=None):
        self.message = message
        self.field = field
        self.value = value
        self.error_code = "E007"
```

### Exception Response Mapping
| Exception Type | HTTP Status | Error Code | Response Format |
|----------------|-------------|------------|-----------------|
| FileUploadException | 400 | E001 | File format/size error |
| FileProcessingException | 500 | E005 | Processing error |
| StorageException | 500 | E006 | Storage error |
| ValidationException | 422 | E007 | Validation error |
| AuthenticationException | 401 | E004 | Authentication error |
| DatabaseException | 500 | E003 | Database error |

### Error Response Structure
```json
{
    "status": "error",
    "error_code": "E005",
    "message": "File processing failed",
    "details": {
        "operation": "core_processing",
        "file_id": 456,
        "error": "Processing timeout after 300 seconds"
    },
    "timestamp": "2025-08-01T10:30:00Z",
    "request_id": "req_123456789"
}
```

---

## Performance Requirements

### Response Time Targets
- **File Upload:** < 30 seconds for 50MB file
- **Processing Time:** < 5 minutes for standard files
- **Database Operations:** < 2 seconds
- **Overall Response:** < 5 minutes total

### Throughput Requirements
- **Concurrent Uploads:** 20 users
- **Files per Hour:** 100 files
- **Storage Capacity:** 1TB total storage
- **Processing Queue:** 50 files in queue

### Resource Usage
- **Memory:** < 500MB per file processing
- **CPU:** < 50% per processing job
- **Storage:** Efficient file compression
- **Network:** Optimized file transfer

### Optimization Techniques
- **Streaming Upload:** Process files in chunks
- **Async Processing:** Background processing for large files
- **File Compression:** Compress files for storage
- **Caching:** Cache frequently accessed data
- **Connection Pooling:** Efficient database connections

---

## Testing Instructions

### Postman Setup

#### 1. Create New Request
- **Method:** POST
- **URL:** `http://localhost:8000/api/v1/files/upload`
- **Headers:**
  ```
  Authorization: Bearer <your_jwt_token>
  Accept: application/json
  ```

#### 2. Request Body (Form Data)
```
file: [Select File] (XLSX or CSV file)
engagement_name: Q1 Financial Analysis
date1: 2025-01-15
date2: 2025-02-15
date3: 2025-03-15
date4: 2025-04-15
```

#### 3. Test Cases

**Test Case 1: Successful File Upload**
- **Description:** Upload valid XLSX file with all required fields
- **Expected Status:** 200 OK
- **Expected Response:** File processing confirmation
- **Validation:**
  - Check file_id is generated
  - Verify processed_flag is true
  - Confirm storage locations are set
  - Check processing time is recorded

**Test Case 2: Invalid File Format**
- **Description:** Upload file with unsupported format
- **Expected Status:** 400 Bad Request
- **Expected Response:** File format error
- **Test Data:** Upload PDF or TXT file
- **Validation:** Error message specifies allowed formats

**Test Case 3: File Too Large**
- **Description:** Upload file exceeding 50MB limit
- **Expected Status:** 413 Payload Too Large
- **Expected Response:** File size error
- **Test Data:** Create file larger than 50MB
- **Validation:** Error includes actual and maximum sizes

**Test Case 4: Missing Required Fields**
- **Description:** Upload file without engagement name
- **Expected Status:** 422 Unprocessable Entity
- **Expected Response:** Validation error
- **Test Data:** Omit engagement_name field
- **Validation:** Error details specify missing field

**Test Case 5: Invalid Date Format**
- **Description:** Upload with invalid date format
- **Expected Status:** 422 Unprocessable Entity
- **Expected Response:** Date validation error
- **Test Data:** `date1: 2025/01/15` (wrong format)
- **Validation:** Error specifies correct date format

**Test Case 6: Unauthorized Access**
- **Description:** Upload file without authentication
- **Expected Status:** 401 Unauthorized
- **Expected Response:** Authentication error
- **Steps:**
  1. Remove Authorization header
  2. Send request
  3. Verify error response

**Test Case 7: Processing Timeout**
- **Description:** Upload very large file that times out
- **Expected Status:** 500 Internal Server Error
- **Expected Response:** Processing timeout error
- **Test Data:** Large file that takes >5 minutes to process
- **Validation:** Error includes timeout information

#### 4. Environment Variables
```json
{
    "base_url": "http://localhost:8000",
    "auth_token": "your_jwt_token_here",
    "test_file_path": "/path/to/test/file.xlsx",
    "test_engagement_name": "Test Engagement"
}
```

#### 5. Pre-request Script
```javascript
// Set up test data
pm.environment.set("test_engagement", pm.environment.get("test_engagement_name"));
pm.environment.set("test_date", "2025-08-01");
```

#### 6. Tests Script
```javascript
// Test successful upload
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has file_id", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.file_id).to.be.a('number');
});

pm.test("File is processed", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.processed_flag).to.be.true;
});

pm.test("Storage locations are set", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.storage_location).to.not.be.empty;
    pm.expect(jsonData.data.input_location).to.not.be.empty;
});

pm.test("Processing time is recorded", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.processing_time_seconds).to.be.a('number');
    pm.expect(jsonData.data.processing_time_seconds).to.be.greaterThan(0);
});

pm.test("Line count is calculated", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.line_count).to.be.a('number');
    pm.expect(jsonData.data.line_count).to.be.greaterThan(0);
});

pm.test("Response structure is correct", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
    pm.expect(jsonData).to.have.property('data');
    pm.expect(jsonData).to.have.property('message');
    pm.expect(jsonData).to.have.property('timestamp');
});

// Performance test
pm.test("Upload time is acceptable", function () {
    pm.expect(pm.response.responseTime).to.be.below(300000); // 5 minutes
});
```

### Automated Testing

#### Unit Test Example
```python
def test_file_upload_success(client, auth_token, test_file):
    """Test successful file upload"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    files = {"file": ("test.xlsx", test_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {
        "engagement_name": "Test Engagement",
        "date1": "2025-01-15",
        "date2": "2025-02-15",
        "date3": "2025-03-15",
        "date4": "2025-04-15"
    }
    
    response = client.post("/api/v1/files/upload", files=files, data=data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["file_id"] is not None
    assert data["data"]["processed_flag"] == True
    assert data["data"]["line_count"] > 0

def test_file_upload_invalid_format(client, auth_token):
    """Test file upload with invalid format"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    files = {"file": ("test.txt", b"test content", "text/plain")}
    data = {
        "engagement_name": "Test Engagement",
        "date1": "2025-01-15",
        "date2": "2025-02-15",
        "date3": "2025-03-15",
        "date4": "2025-04-15"
    }
    
    response = client.post("/api/v1/files/upload", files=files, data=data, headers=headers)
    
    assert response.status_code == 400
    data = response.json()
    assert "Invalid file format" in data["message"]
```

#### Integration Test Example
```python
def test_file_upload_processing_workflow(client, auth_token, large_test_file):
    """Test complete file upload and processing workflow"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    files = {"file": ("large_test.xlsx", large_test_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {
        "engagement_name": "Large File Test",
        "date1": "2025-01-15",
        "date2": "2025-02-15",
        "date3": "2025-03-15",
        "date4": "2025-04-15"
    }
    
    # Upload file
    response = client.post("/api/v1/files/upload", files=files, data=data, headers=headers)
    
    assert response.status_code == 200
    upload_data = response.json()
    file_id = upload_data["data"]["file_id"]
    
    # Verify file was processed
    assert upload_data["data"]["processed_flag"] == True
    assert upload_data["data"]["processing_time_seconds"] > 0
    
    # Check file exists in storage
    storage_path = upload_data["data"]["storage_location"]
    assert os.path.exists(storage_path)
```

---

## Monitoring and Alerts

### Key Metrics to Monitor
- **Upload Success Rate:** > 95%
- **Processing Success Rate:** > 90%
- **Average Processing Time:** < 3 minutes
- **Storage Usage:** < 80% of capacity

### Alert Conditions
- **High Upload Failure Rate:** > 10% in 5 minutes
- **Processing Failures:** > 15% in 10 minutes
- **Slow Processing:** Average > 5 minutes for 10 files
- **Storage Space:** > 90% capacity used

### Performance Monitoring
- **File Upload Speed:** Monitor upload times
- **Processing Queue:** Track queue length
- **Storage I/O:** Monitor disk performance
- **Memory Usage:** Track memory consumption

---

## Deployment Considerations

### Environment Variables
```bash
# File Upload
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=xlsx,csv
UPLOAD_DIR=/opt/landrover
TEMP_DIR=/tmp/geopulse_uploads

# Processing
PROCESSING_TIMEOUT_SECONDS=300
MAX_CONCURRENT_PROCESSING=10
PROCESSING_MEMORY_LIMIT_MB=500

# Storage
STORAGE_PATH=/opt/landrover
BACKUP_PATH=/opt/backups/geopulse
RETENTION_DAYS=90

# Database
DATABASE_URL=postgresql://geopulse_user:password123@localhost:5432/geopulse_db

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/geopulse/file_upload.log
```

### Dependencies
- PostgreSQL 15+
- Python 3.11+
- FastAPI 0.104+
- pandas 2.0+
- openpyxl 3.0+
- SQLAlchemy 2.0+
- PyJWT 2.8+

### Health Checks
- File system permissions
- Storage space availability
- Database connectivity
- Processing queue status
- Memory and CPU usage
