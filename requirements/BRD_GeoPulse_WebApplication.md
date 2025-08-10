# Business Requirements Document (BRD)
## GeoPulse Web Application

**Document Version:** 1.0  
**Date:** August 2025  
**Project:** GeoPulse  
**Document Type:** Business Requirements Document  

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Project Overview](#project-overview)
3. [Business Objectives](#business-objectives)
4. [Functional Requirements](#functional-requirements)
5. [Technical Requirements](#technical-requirements)
6. [User Interface Requirements](#user-interface-requirements)
7. [API Specifications](#api-specifications)
8. [Database Requirements](#database-requirements)
9. [Security Requirements](#security-requirements)
10. [Performance Requirements](#performance-requirements)
11. [Operational Requirements](#operational-requirements)
12. [Testing Requirements](#testing-requirements)
13. [Documentation Requirements](#documentation-requirements)
14. [Assumptions and Constraints](#assumptions-and-constraints)
15. [Appendices](#appendices)

---

## Executive Summary

GeoPulse is a web-based application designed to provide file processing and analytics capabilities for organizations. The system allows users to register, upload data files (XLSX/CSV), process them through core business logic, and view results with conditional formatting. The application includes user management, file storage, processing workflows, and comprehensive reporting features.

**Key Features:**
- User registration and authentication system
- File upload and processing capabilities
- Dashboard with transaction history
- Advanced search and filtering
- Real-time processing status tracking
- Comprehensive logging and error handling

---

## Project Overview

### Purpose
The GeoPulse application serves as a centralized platform for organizations to process and analyze their data files through automated workflows, providing insights and formatted results for business decision-making.

### Scope
The application encompasses:
- User management and authentication
- File upload and validation
- Data processing workflows
- Results visualization
- Transaction history and search
- Administrative functions

### Stakeholders
- **Primary Users:** Organization employees who need to process data files
- **Administrators:** System administrators managing user access and system configuration
- **Developers:** Technical team responsible for implementation and maintenance

---

## Business Objectives

### Primary Objectives
1. **Streamline Data Processing:** Provide an automated platform for processing XLSX and CSV files
2. **Enhance User Experience:** Create an intuitive interface for file upload and result retrieval
3. **Improve Data Security:** Implement secure user authentication and file storage
4. **Enable Scalability:** Design a system that can handle multiple users and large file volumes
5. **Provide Analytics:** Offer insights into usage patterns and processing metrics

### Success Criteria
- 99.9% system uptime
- File processing completion within 5 minutes for files up to 10MB
- User satisfaction score of 4.5/5 or higher
- Zero data loss during processing
- Successful processing of 95% of uploaded files

---

## Functional Requirements

### 1. User Registration System

#### 1.1 Registration Process
- **FR-1.1:** Users must be able to register with the following information:
  - Organization name (required)
  - User name (required)
  - Contact phone (required)
  - Email address (required)
  - Organization logo (optional - defaults to "datalegos" logo)

#### 1.2 User ID Generation
- **FR-1.2:** System must automatically generate a unique user ID upon successful registration

#### 1.3 Data Storage
- **FR-1.3:** Registration data must be stored in PostgreSQL database
- **FR-1.4:** User details must be written to a JSON file named after the user's name

### 2. Authentication System

#### 2.1 Login Functionality
- **FR-2.1:** Users must be able to log in using their registered credentials
- **FR-2.2:** System must implement JWT-based authentication
- **FR-2.3:** Session management must be secure and time-limited

### 3. Dashboard and Navigation

#### 3.1 Dashboard Access
- **FR-3.1:** Upon successful login, users must be directed to the dashboard
- **FR-3.2:** Dashboard must display all user file names in tabular format

#### 3.2 Navigation Structure
- **FR-3.3:** Top panel must include the following tabs:
  - New Upload
  - Past Uploads
  - Profile
  - Usage and Limits
  - Messages

#### 3.4 User Logo Display
- **FR-3.4:** Top panel must display the customer logo (uploaded during registration)

### 4. File Upload and Processing

#### 4.1 File Upload Interface
- **FR-4.1:** Users must be able to select files for upload
- **FR-4.2:** System must validate file format (XLSX or CSV only)
- **FR-4.3:** Users must provide engagement name for search purposes
- **FR-4.4:** Users must select 4 dates during upload process
- **FR-4.5:** Submit button must trigger API call for processing

#### 4.2 File Storage
- **FR-4.6:** Input files must be stored permanently at: `/opt/landrover/userid/<date>/input/`
- **FR-4.7:** Output files must be stored at: `/opt/landrover/userid/<date>/output/`
- **FR-4.8:** Output files must be in XLS or XLSX format with conditional formatting

#### 4.3 Processing Workflow
- **FR-4.9:** System must execute core business logic on input files
- **FR-4.10:** Processing must include inference columns with conditional formatting
- **FR-4.11:** Results must be displayed back to the UI after processing

### 5. Transaction Management

#### 5.1 Transaction History
- **FR-5.1:** Users must be able to view all previous transactions
- **FR-5.2:** Transaction display must include file uploads and their dates
- **FR-5.3:** Users must be able to click on individual transactions

#### 5.2 Search Functionality
- **FR-5.4:** Users must be able to search transactions by:
  - Transaction name
  - Upload date
- **FR-5.5:** Search results must maintain layout of left, top, and right panels

### 6. Metrics and Analytics

#### 6.1 Usage Metrics
- **FR-6.1:** System must track and display:
  - Count of file uploads
  - Number of lines in each file (excluding headers)
- **FR-6.2:** Metrics must be accessible through dedicated API

---

## Technical Requirements

### 1. Technology Stack

#### 1.1 Backend
- **Programming Language:** Python
- **Database:** PostgreSQL
- **Authentication:** JWT (JSON Web Tokens)
- **File Processing:** Support for XLSX and CSV formats

#### 1.2 Frontend
- **Framework:** Web-based interface
- **File Validation:** Client-side and server-side validation
- **Responsive Design:** Support for multiple screen sizes

#### 1.3 Infrastructure
- **Containerization:** Docker for PostgreSQL
- **File Storage:** Local file system with organized directory structure
- **Volume Sharing:** Docker volumes mapped to `/opt` folder

### 2. Database Design

#### 2.1 Required Tables
- **Users Table:** Store user registration information
- **Files Table:** Store file upload and processing metadata

#### 2.2 Database Schema Requirements
- **User ID:** Auto-generated unique identifier
- **File Metadata:** User, date, filename, line count, storage location, processed_flag
- **Audit Fields:** Creation timestamps, modification timestamps

### 3. File System Requirements

#### 3.1 Directory Structure
```
/opt/landrover/
├── userid/
│   ├── <date>/
│   │   ├── input/
│   │   └── output/
```

#### 3.2 File Naming Conventions
- Input files: Original filename preserved
- Output files: Processed results in XLS/XLSX format
- User files: JSON format named after user

### 4. Configuration Management

#### 4.1 Environment Configuration
- **Primary Config:** `environment.yml`
- **Function-specific Configs:** `environment_<functionalityname>.yml`
- **Network Config:** Database and API settings
- **Program Config:** Control parameters (as needed)

#### 4.2 CLI Integration
- All CLI commands must be consolidated in README.md
- Configuration parameters must be integrated into Python CLI commands

---

## User Interface Requirements

### 1. General UI Guidelines

#### 1.1 User Experience
- **UI-1.1:** Clear and intuitive navigation
- **UI-1.2:** Consistent design language across all screens
- **UI-1.3:** Responsive design for various screen sizes
- **UI-1.4:** Clear error messages with unique error IDs

#### 1.2 Layout Requirements
- **UI-1.5:** Maintain left, top, and right panel layout
- **UI-1.6:** Top panel must display customer logo
- **UI-1.7:** Tab-based navigation in top panel

### 2. Screen-Specific Requirements

#### 2.1 Registration Screen
- **UI-2.1:** Form fields for all required registration information
- **UI-2.2:** File upload capability for organization logo
- **UI-2.3:** Validation messages for required fields
- **UI-2.4:** Success confirmation upon registration

#### 2.2 Login Screen
- **UI-2.5:** Username/email and password fields
- **UI-2.6:** "Remember me" functionality (optional)
- **UI-2.7:** Password reset capability (future enhancement)

#### 2.3 Dashboard Screen
- **UI-2.8:** Tabular display of user files
- **UI-2.9:** Quick access to upload functionality
- **UI-2.10:** Transaction history overview

#### 2.4 File Upload Screen
- **UI-2.11:** Drag-and-drop file selection
- **UI-2.12:** File format validation indicators
- **UI-2.13:** Engagement name input field
- **UI-2.14:** Date selection interface (4 dates)
- **UI-2.15:** Progress indicators during upload
- **UI-2.16:** Submit button with confirmation

#### 2.5 Transaction History Screen
- **UI-2.17:** List/grid view of past transactions
- **UI-2.18:** Search and filter controls
- **UI-2.19:** Clickable transaction items
- **UI-2.20:** Date range selection

---

## API Specifications

### 1. API-1: User Registration
- **Endpoint:** `POST /api/register`
- **Purpose:** Handle user registration and data storage
- **Input:** User registration details
- **Output:** User ID and confirmation
- **Database Operations:** Insert user record
- **File Operations:** Create JSON user file

### 2. API-2: User Authentication
- **Endpoint:** `POST /api/login`
- **Purpose:** Authenticate user and generate JWT
- **Input:** Username/email and password
- **Output:** JWT token and user information
- **Security:** JWT-based authentication

### 3. API-3: Dashboard Data
- **Endpoint:** `GET /api/dashboard`
- **Purpose:** Retrieve user file names for dashboard display
- **Input:** User ID (from JWT)
- **Output:** List of user files in tabular format
- **Authentication:** Required

### 4. API-4: File Upload Processing
- **Endpoint:** `POST /api/upload`
- **Purpose:** Handle file upload and initiate processing
- **Input:** File, engagement name, dates, user ID
- **Output:** Upload confirmation and processing status
- **File Storage:** `/opt/landrover/userid/<date>/input/`

### 5. API-5: File Storage and Metadata
- **Endpoint:** `POST /api/store-file`
- **Purpose:** Store uploaded file and update database
- **Input:** File path, user ID, metadata
- **Output:** Storage confirmation and file path
- **Database:** Update files table with metadata
- **Advanced:** Capture browser IP and location (if possible)

### 6. API-6: Core Processing
- **Endpoint:** `POST /api/process`
- **Purpose:** Execute core business logic on input file
- **Input:** Input file path
- **Output:** Output file path
- **Processing:** Core business logic execution
- **Output Format:** XLS/XLSX with conditional formatting

### 7. API-7: Results Display
- **Endpoint:** `GET /api/results/{file_id}`
- **Purpose:** Retrieve and display processing results
- **Input:** File ID
- **Output:** Formatted results for UI display
- **Authentication:** Required

### 8. API-8: Metrics
- **Endpoint:** `GET /api/metrics`
- **Purpose:** Retrieve usage and processing metrics
- **Input:** User ID (from JWT)
- **Output:** Upload counts, line counts, processing statistics
- **Authentication:** Required

---

## Database Requirements

### 1. PostgreSQL Setup

#### 1.1 Installation
- **DBA-1.1:** Docker-based PostgreSQL installation
- **DBA-1.2:** Installation script for automated setup
- **DBA-1.3:** Volume sharing to `/opt` folder

#### 1.2 Configuration
- **DBA-1.4:** Database backup configuration
- **DBA-1.5:** Connection pooling setup
- **DBA-1.6:** Performance optimization

### 2. Table Design

#### 2.1 Users Table
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    organization_name VARCHAR(255) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    logo_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.2 Files Table
```sql
CREATE TABLE files (
    file_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    upload_date DATE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    line_count INTEGER,
    storage_location VARCHAR(500) NOT NULL,
    processed_flag BOOLEAN DEFAULT FALSE,
    engagement_name VARCHAR(255),
    browser_ip VARCHAR(45),
    browser_location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Security Requirements

### 1. Authentication and Authorization
- **SEC-1.1:** JWT-based authentication for all API endpoints
- **SEC-1.2:** Secure password storage (hashed)
- **SEC-1.3:** Session timeout configuration
- **SEC-1.4:** Role-based access control (future enhancement)

### 2. Data Protection
- **SEC-2.1:** Encrypted file storage
- **SEC-2.2:** Secure file upload validation
- **SEC-2.3:** Input sanitization and validation
- **SEC-2.4:** SQL injection prevention

### 3. Network Security
- **SEC-3.1:** HTTPS enforcement
- **SEC-3.2:** CORS configuration
- **SEC-3.3:** Rate limiting on API endpoints
- **SEC-3.4:** IP address logging (if possible)

---

## Performance Requirements

### 1. Response Times
- **PERF-1.1:** Page load times < 3 seconds
- **PERF-1.2:** API response times < 2 seconds
- **PERF-1.3:** File upload processing < 5 minutes (for files up to 10MB)

### 2. Scalability
- **PERF-2.1:** Support for 100+ concurrent users
- **PERF-2.2:** Handle files up to 50MB
- **PERF-2.3:** Database connection pooling

### 3. Availability
- **PERF-3.1:** 99.9% system uptime
- **PERF-3.2:** Graceful error handling
- **PERF-3.3:** Automatic retry mechanisms

---

## Operational Requirements

### 1. Logging and Monitoring
- **OPS-1.1:** Comprehensive logging for all operations
- **OPS-1.2:** Error tracking with unique error IDs
- **OPS-1.3:** Performance monitoring
- **OPS-1.4:** User activity tracking

### 2. Error Handling
- **OPS-2.1:** Exception handling for all external calls
- **OPS-2.2:** User-friendly error messages
- **OPS-2.3:** Error recovery mechanisms
- **OPS-2.4:** Error reporting and alerting

### 3. Backup and Recovery
- **OPS-3.1:** Automated database backups
- **OPS-3.2:** File system backups
- **OPS-3.3:** Disaster recovery procedures
- **OPS-3.4:** Data retention policies

---

## Testing Requirements

### 1. Unit Testing
- **TEST-1.1:** Unit test cases for each function
- **TEST-1.2:** 90% code coverage minimum
- **TEST-1.3:** Automated test execution
- **TEST-1.4:** Test data management

### 2. Integration Testing
- **TEST-2.1:** API endpoint testing
- **TEST-2.2:** Database integration testing
- **TEST-2.3:** File processing workflow testing
- **TEST-2.4:** Authentication flow testing

### 3. User Acceptance Testing
- **TEST-3.1:** End-to-end workflow testing
- **TEST-3.2:** User interface testing
- **TEST-3.3:** Performance testing
- **TEST-3.4:** Security testing

---

## Documentation Requirements

### 1. Technical Documentation
- **DOC-1.1:** Updated README.md file
- **DOC-1.2:** API documentation
- **DOC-1.3:** Database schema documentation
- **DOC-1.4:** Deployment guide

### 2. User Documentation
- **DOC-2.1:** User manual
- **DOC-2.2:** System administration guide
- **DOC-2.3:** Troubleshooting guide
- **DOC-2.4:** FAQ document

### 3. Operational Documentation
- **DOC-3.1:** Installation procedures
- **DOC-3.2:** Configuration management
- **DOC-3.3:** Monitoring and alerting procedures
- **DOC-3.4:** Backup and recovery procedures

---

## Assumptions and Constraints

### Assumptions
1. **A-1:** Users have basic computer literacy
2. **A-2:** Files uploaded are legitimate business data
3. **A-3:** Network connectivity is stable
4. **A-4:** Server resources are adequate for processing
5. **A-5:** Users will follow file format requirements

### Constraints
1. **C-1:** File size limited to 50MB maximum
2. **C-2:** Supported file formats: XLSX and CSV only
3. **C-3:** Processing time may vary based on file size
4. **C-4:** Browser compatibility with modern browsers only
5. **C-5:** Network bandwidth limitations for file uploads

### Dependencies
1. **D-1:** PostgreSQL database availability
2. **D-2:** File system storage capacity
3. **D-3:** Network connectivity
4. **D-4:** Python environment and dependencies
5. **D-5:** Docker containerization support

---

## Appendices

### Appendix A: Error Code Definitions
- **E001:** File format not supported
- **E002:** File size exceeds limit
- **E003:** Database connection failed
- **E004:** Authentication failed
- **E005:** Processing timeout
- **E006:** Storage space insufficient
- **E007:** Invalid user input
- **E008:** System maintenance mode

### Appendix B: Configuration Parameters
- **Database Connection:** Host, port, database name, credentials
- **File Storage:** Base path, size limits, retention policies
- **Authentication:** JWT secret, token expiration, session timeout
- **Processing:** Timeout values, retry attempts, batch sizes
- **Logging:** Log levels, file paths, rotation policies

### Appendix C: API Response Formats
- **Success Response:**
```json
{
    "status": "success",
    "data": {},
    "message": "Operation completed successfully"
}
```

- **Error Response:**
```json
{
    "status": "error",
    "error_code": "E001",
    "message": "File format not supported",
    "timestamp": "2024-12-01T10:00:00Z"
}
```

### Appendix D: File Processing Workflow
1. File upload and validation
2. Storage in input directory
3. Database metadata update
4. Core processing execution
5. Output file generation
6. Results formatting and display
7. Transaction history update

---

**Document Approval:**
- **Business Analyst:** [Name] - [Date]
- **Technical Lead:** [Name] - [Date]
- **Project Manager:** [Name] - [Date]
- **Stakeholder:** [Name] - [Date]

**Document Control:**
- **Version:** 1.0
- **Last Updated:** December 2024
- **Next Review:** January 2025
- **Distribution:** Development Team, Business Stakeholders, QA Team
