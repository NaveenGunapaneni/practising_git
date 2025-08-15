# GeoPulse API - Postman Test Collection

This comprehensive Postman collection tests all endpoints and scenarios of the GeoPulse API.

## 📁 Files Included

1. **`GeoPulse_API_Complete_Test_Collection.postman_collection.json`** - Main test collection
2. **`GeoPulse_API_Environment.postman_environment.json`** - Environment variables
3. **`sample_data.csv`** - Sample CSV file for testing uploads
4. **`invalid_file.txt`** - Invalid file type for testing validation

## 🚀 Quick Setup

### 1. Import Collection and Environment

1. Open Postman
2. Click **Import** button
3. Import both JSON files:
   - `GeoPulse_API_Complete_Test_Collection.postman_collection.json`
   - `GeoPulse_API_Environment.postman_environment.json`

### 2. Set Environment

1. Select **"GeoPulse API Environment"** from the environment dropdown
2. Verify `base_url` is set to `http://localhost:8000`

### 3. Prepare Test Files

1. Create a sample XLSX file or use the provided CSV file
2. Place test files in an accessible location for file uploads

## 📋 Test Collection Structure

### 🏠 Root & System Info
- **Root - Service Overview**: Tests the HTML homepage
- **Middleware Info**: Tests system middleware information

### 🏥 Health Checks
- **Basic Health Check**: Tests `/api/v1/health`
- **Detailed Health Check**: Tests `/api/v1/health/detailed` with database connectivity

### 🔐 Authentication
- **User Registration - Success**: Creates a new user with unique email
- **User Registration - Duplicate Email**: Tests duplicate email validation
- **User Registration - Invalid Data**: Tests input validation
- **User Login - Success (JSON)**: Tests JSON login format
- **User Login - Success (Form Data)**: Tests form-encoded login
- **User Login - Invalid Credentials**: Tests authentication failure

### 📁 File Management
- **File Upload - Success (XLSX)**: Tests successful XLSX file upload
- **File Upload - Success (CSV)**: Tests successful CSV file upload
- **File Upload - No Authentication**: Tests authentication requirement
- **File Upload - Invalid File Type**: Tests file type validation
- **List User Files**: Tests file listing with pagination
- **Get File Status**: Tests individual file status retrieval
- **Get File Status - Not Found**: Tests 404 error handling
- **Test Upload Endpoint**: Tests debug upload endpoint

### 📊 Dashboard
- **Get Dashboard Data - Default**: Tests default dashboard view
- **Get Dashboard Data - With Filters**: Tests filtered dashboard
- **Get Dashboard Data - Processed Files Only**: Tests status filtering
- **Get Dashboard Data - No Authentication**: Tests authentication requirement

## 🔄 Test Flow & Dependencies

### Recommended Execution Order:

1. **Health Checks** (Independent)
2. **Authentication** (Sequential - creates user and gets token)
3. **File Management** (Requires auth token from step 2)
4. **Dashboard** (Requires auth token and uploaded files)

### Automatic Variable Management:

The collection automatically manages these environment variables:
- `unique_email` - Generated unique email for registration
- `test_email` - Stored email for login tests
- `auth_token` - JWT token from successful login
- `user_id` - User ID from registration
- `file_id` - File ID from successful upload
- `csv_file_id` - CSV file ID from CSV upload
- `test_engagement` - Generated engagement name

## 🧪 Test Scenarios Covered

### ✅ Success Scenarios
- User registration with valid data
- User login with correct credentials (JSON & Form)
- File upload with XLSX and CSV files
- File processing and status tracking
- Dashboard data retrieval with various filters
- Health checks and system monitoring

### ❌ Error Scenarios
- Duplicate email registration
- Invalid input data validation
- Authentication failures
- Unauthorized access attempts
- Invalid file type uploads
- File not found errors
- Missing authentication tokens

### 🔍 Validation Tests
- Response status codes
- Response structure validation
- Data type verification
- Required field presence
- Business logic validation
- Error message accuracy

## 📊 Test Assertions

Each request includes comprehensive test assertions:

```javascript
// Status code validation
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});

// Response structure validation
pm.test('Response has correct structure', function () {
    const data = pm.response.json();
    pm.expect(data).to.have.property('status', 'success');
    pm.expect(data).to.have.property('data');
});

// Business logic validation
pm.test('File is processed', function () {
    const data = pm.response.json();
    pm.expect(data.data.processed_flag).to.be.true;
});
```

## 🛠️ Customization

### Environment Variables

You can customize the environment by modifying:

```json
{
    "key": "base_url",
    "value": "http://localhost:8000"  // Change for different environments
}
```

### Test Data

Modify request bodies to test different scenarios:

```json
{
    "organization_name": "Your Organization",
    "user_name": "Your Name",
    "contact_phone": "+1-555-0123",
    "email": "your.email@example.com",
    "password": "YourSecurePassword123!"
}
```

## 🚨 Prerequisites

### 1. API Server Running
```bash
# Start the GeoPulse API
cd /path/to/geopulse-api
source geopulse_env/bin/activate
python main.py
```

### 2. Database Running
```bash
# Start PostgreSQL with Docker
cd database
docker-compose up -d
```

### 3. Test Files Available
- Prepare XLSX or CSV files for upload testing
- Ensure files are under 50MB size limit
- Have invalid file types ready for validation testing

## 📈 Running Tests

### Individual Request Testing
1. Select any request from the collection
2. Click **Send**
3. Review response and test results in the **Test Results** tab

### Collection Runner
1. Click on the collection name
2. Click **Run collection**
3. Select requests to run
4. Configure iterations and delays
5. Click **Run GeoPulse API - Complete Test Suite**

### Automated Testing
```bash
# Using Newman (Postman CLI)
npm install -g newman
newman run GeoPulse_API_Complete_Test_Collection.postman_collection.json \
    -e GeoPulse_API_Environment.postman_environment.json \
    --reporters cli,html \
    --reporter-html-export test-results.html
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure API server is running on `http://localhost:8000`
   - Check if port 8000 is available

2. **Database Connection Errors**
   - Verify PostgreSQL container is running
   - Check database health with `/api/v1/health/detailed`

3. **Authentication Failures**
   - Run authentication tests in sequence
   - Verify JWT token is stored in environment variables

4. **File Upload Issues**
   - Ensure test files exist and are accessible
   - Check file size limits (50MB max)
   - Verify file types are supported (.xlsx, .csv, .xls)

### Debug Tips

1. **Check Environment Variables**
   - View current environment values in Postman
   - Verify tokens and IDs are properly stored

2. **Review Console Logs**
   - Open Postman Console (View → Show Postman Console)
   - Check for detailed error messages

3. **API Server Logs**
   - Monitor API server console output
   - Check for detailed error traces

## 📝 Test Results

After running the collection, you'll get:
- ✅ **Pass/Fail status** for each test
- 📊 **Response times** and performance metrics
- 🔍 **Detailed assertions** results
- 📋 **Summary report** with overall statistics

## 🔄 Continuous Integration

For CI/CD integration:

```yaml
# GitHub Actions example
- name: Run API Tests
  run: |
    newman run GeoPulse_API_Complete_Test_Collection.postman_collection.json \
        -e GeoPulse_API_Environment.postman_environment.json \
        --reporters cli,junit \
        --reporter-junit-export test-results.xml
```

## 📞 Support

If you encounter issues:
1. Check the API server logs
2. Verify database connectivity
3. Review environment variable values
4. Ensure all prerequisites are met

Happy Testing! 🚀