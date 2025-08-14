# GeoPulse API - Clean Postman Testing Guide

## Overview

This guide provides streamlined instructions for testing all 4 GeoPulse APIs using a single, clean Postman collection with essential tests only.

## Files Included

### Postman Collections
- **`GeoPulse-API-Testing/`** - Single folder containing all testing files
  - `GeoPulse-Complete-API-Tests.postman_collection.json` - Complete collection with all 4 APIs
  - `GeoPulse-Environment.postman_environment.json` - Environment variables
  - `README.md` - Quick setup guide

### Collection Structure

```
GeoPulse API - Complete Test Suite
├── API-1: User Registration
│   ├── Success Scenarios
│   │   └── Test Case 1: Successful Registration
│   └── Failure Scenarios
│       ├── Test Case 2: Duplicate Email
│       ├── Test Case 3: Invalid Email Format
│       ├── Test Case 4: Missing Required Fields
│       └── Test Case 5: Weak Password
├── API-2: User Authentication
│   ├── Success Scenarios
│   │   └── Test Case 1: Successful Login
│   └── Failure Scenarios
│       ├── Test Case 2: Invalid Password
│       ├── Test Case 3: Non-existent User
│       ├── Test Case 4: Invalid Email Format
│       └── Test Case 5: Missing Password
├── API-3: Dashboard Data
│   ├── Success Scenarios
│   │   ├── Test Case 1: Successful Dashboard Access
│   │   ├── Test Case 2: Dashboard with Pagination
│   │   ├── Test Case 3: Dashboard with Status Filter
│   │   └── Test Case 4: Dashboard with Sorting
│   └── Failure Scenarios
│       ├── Test Case 5: Unauthorized Dashboard Access
│       ├── Test Case 6: Invalid Token
│       └── Test Case 7: Invalid Query Parameters
└── API-4: File Upload Processing
    ├── Success Scenarios
    │   ├── Test Case 1: Successful File Upload
    │   ├── Get File Status
    │   ├── Get User Files List
    │   └── Download Processed File
    └── Failure Scenarios
        ├── Test Case 2: Invalid File Format
        ├── Test Case 3: Missing Required Fields
        ├── Test Case 4: Invalid Date Format
        ├── Test Case 5: Unauthorized File Upload
        └── Test Case 6: Invalid File ID for Status
```

## Setup Instructions

### 1. Import Collections and Environment

1. **Open Postman**
2. **Import Collections**:
   - Click "Import" button
   - Import `GeoPulse_Complete_API_Collection.postman_collection.json`
   - Import `GeoPulse_Dashboard_Complete.postman_collection.json`
   - Import `GeoPulse_FileUpload_Complete.postman_collection.json`
3. **Import Environment**:
   - Import `GeoPulse_Complete_Environment.postman_environment.json`
4. **Select Environment**:
   - Choose "GeoPulse Complete Test Environment" from the environment dropdown

### 2. Verify Environment Variables

Ensure these variables are set in your environment:

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `base_url` | `http://127.0.0.1:8000` | GeoPulse API base URL |
| `unique_email` | (auto-generated) | Unique email for testing |
| `test_password` | `SecurePassword123!` | Test user password |
| `auth_token` | (auto-set) | JWT authentication token |
| `user_id` | (auto-set) | Created user ID |
| `file_id` | (auto-set) | Uploaded file ID |
| `test_engagement_name` | `Test Engagement` | Default engagement name |
| `test_date1-4` | `2025-01-15` etc. | Test dates for file upload |

### 3. Start GeoPulse Application

```bash
cd geopulse
python main.py
```

Verify the application is running by accessing: `http://127.0.0.1:8000/api/v1/health`

## Testing Workflow

### Recommended Testing Sequence

#### Phase 1: User Registration (API-1)
1. **Run Success Scenario First**:
   - Execute "Test Case 1: Successful Registration"
   - This will create a test user and set `user_id` and `unique_email` variables

2. **Run Failure Scenarios**:
   - Test Case 2: Duplicate Email (uses same email from success case)
   - Test Case 3: Invalid Email Format
   - Test Case 4: Missing Required Fields
   - Test Case 5: Weak Password

#### Phase 2: User Authentication (API-2)
1. **Run Success Scenario**:
   - Execute "Test Case 1: Successful Login"
   - This will authenticate the user and set `auth_token` variable

2. **Run Failure Scenarios**:
   - Test Case 2: Invalid Password
   - Test Case 3: Non-existent User
   - Test Case 4: Invalid Email Format
   - Test Case 5: Missing Password

#### Phase 3: Dashboard Data (API-3)
1. **Run Success Scenarios**:
   - Test Case 1: Successful Dashboard Access
   - Test Case 2: Dashboard with Pagination
   - Test Case 3: Dashboard with Status Filter
   - Test Case 4: Dashboard with Sorting

2. **Run Failure Scenarios**:
   - Test Case 5: Unauthorized Dashboard Access
   - Test Case 6: Invalid Token
   - Test Case 7: Invalid Query Parameters

#### Phase 4: File Upload Processing (API-4)
1. **Prepare Test Files**:
   - Ensure you have `sample_properties_for_geopulse.csv` in your project root
   - Create an `invalid_file.txt` for testing invalid formats

2. **Run Success Scenarios**:
   - Test Case 1: Successful File Upload (sets `file_id` variable)
   - Get File Status
   - Get User Files List
   - Download Processed File

3. **Run Failure Scenarios**:
   - Test Case 2: Invalid File Format
   - Test Case 3: Missing Required Fields
   - Test Case 4: Invalid Date Format
   - Test Case 5: Unauthorized File Upload
   - Test Case 6: Invalid File ID for Status

## Test Case Details

### API-1: User Registration

#### Success Scenarios
- **Test Case 1**: Creates a new user with valid data
  - Generates unique email automatically
  - Validates response structure and user_id generation
  - Sets environment variables for subsequent tests

#### Failure Scenarios
- **Test Case 2**: Tests duplicate email validation
- **Test Case 3**: Tests email format validation
- **Test Case 4**: Tests required field validation
- **Test Case 5**: Tests password strength validation

### API-2: User Authentication

#### Success Scenarios
- **Test Case 1**: Authenticates user and retrieves JWT token
  - Validates token structure and expiration
  - Sets auth_token for protected endpoints

#### Failure Scenarios
- **Test Case 2**: Tests invalid password handling
- **Test Case 3**: Tests non-existent user handling
- **Test Case 4**: Tests email format validation
- **Test Case 5**: Tests missing password validation

### API-3: Dashboard Data

#### Success Scenarios
- **Test Case 1**: Retrieves complete dashboard data
- **Test Case 2**: Tests pagination functionality
- **Test Case 3**: Tests status filtering
- **Test Case 4**: Tests sorting functionality

#### Failure Scenarios
- **Test Case 5**: Tests unauthorized access
- **Test Case 6**: Tests invalid token handling
- **Test Case 7**: Tests parameter validation

### API-4: File Upload Processing

#### Success Scenarios
- **Test Case 1**: Uploads and processes a file
- **Get File Status**: Retrieves file processing status
- **Get User Files List**: Lists all user files
- **Download Processed File**: Downloads processed file

#### Failure Scenarios
- **Test Case 2**: Tests invalid file format handling
- **Test Case 3**: Tests missing required fields
- **Test Case 4**: Tests invalid date format
- **Test Case 5**: Tests unauthorized upload
- **Test Case 6**: Tests invalid file ID handling

## Expected Results

### Success Criteria
All tests should pass with the following results:

#### API-1 Registration
- ✅ Status 201 for successful registration
- ✅ Status 400 for duplicate email
- ✅ Status 422 for validation errors

#### API-2 Authentication
- ✅ Status 200 for successful login with JWT token
- ✅ Status 401 for invalid credentials
- ✅ Status 422 for validation errors

#### API-3 Dashboard
- ✅ Status 200 for successful data retrieval
- ✅ Proper pagination, filtering, and sorting
- ✅ Status 401 for unauthorized access
- ✅ Status 422 for invalid parameters

#### API-4 File Upload
- ✅ Status 200 for successful upload and processing
- ✅ Status 400 for invalid file formats
- ✅ Status 422 for validation errors
- ✅ Status 401 for unauthorized access

### Performance Expectations
- Registration: < 3 seconds
- Login: < 1 second
- Dashboard: < 1 second
- File Upload: < 5 minutes (depending on file size)

## Troubleshooting

### Common Issues

1. **Application Not Running**
   ```
   Error: connect ECONNREFUSED 127.0.0.1:8000
   ```
   **Solution**: Start the GeoPulse application with `python main.py`

2. **Authentication Failures**
   ```
   Status: 401 Unauthorized
   ```
   **Solution**: Ensure registration and login tests pass first to set auth_token

3. **File Upload Issues**
   ```
   Status: 400 Bad Request - File format error
   ```
   **Solution**: Ensure test files exist and have correct formats (.csv, .xlsx)

4. **Environment Variables Not Set**
   ```
   Variables like {{auth_token}} not resolved
   ```
   **Solution**: Run tests in sequence to auto-populate variables

### Debug Steps

1. **Check Environment**: Verify correct environment is selected
2. **Check Variables**: Ensure variables are populated after successful tests
3. **Check Application Logs**: Review `geopulse/logs/api.log` for errors
4. **Check Test Order**: Run tests in the recommended sequence

## Advanced Testing

### Running Collections with Newman

Install Newman (Postman CLI):
```bash
npm install -g newman
```

Run collections:
```bash
# Run complete collection
newman run GeoPulse-API-Testing/GeoPulse-Complete-API-Tests.postman_collection.json \
  -e GeoPulse-API-Testing/GeoPulse-Environment.postman_environment.json
```

### Automated Testing Pipeline

Create a test script:
```bash
#!/bin/bash
echo "Starting GeoPulse API Tests..."

# Run tests in sequence
newman run GeoPulse-API-Testing/GeoPulse-Complete-API-Tests.postman_collection.json \
  -e GeoPulse-API-Testing/GeoPulse-Environment.postman_environment.json \
  --reporters cli,json \
  --reporter-json-export results.json

echo "All tests completed!"
```

## Conclusion

This comprehensive Postman collection provides complete test coverage for all 4 GeoPulse APIs with both success and failure scenarios. The organized folder structure makes it easy to:

- Test individual APIs or specific scenarios
- Run complete test suites
- Validate all error conditions
- Ensure proper API behavior
- Monitor performance and reliability

Follow the recommended testing sequence for best results, and use the troubleshooting guide to resolve any issues that arise during testing.