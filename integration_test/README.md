# GeoPulse Integration Testing Framework

This directory contains a comprehensive integration testing framework for the GeoPulse application. The framework tests the complete application workflow including API endpoints, UI interactions, and end-to-end functionality.

## 🎯 Overview

The integration tests cover the following workflow:

1. **API Health Check** - Verify API is running and healthy
2. **User Registration** - Test user registration through API
3. **User Login** - Test user authentication
4. **Dashboard Access** - Verify dashboard functionality
5. **File Upload** - Test file upload functionality
6. **File Processing** - Wait for and verify file processing
7. **File Download** - Test downloading processed files
8. **File Validation** - Validate downloaded file format and content
9. **UI Testing** - Test all functionality through the web interface
10. **Error Handling** - Test error scenarios and edge cases

## 📁 Directory Structure

```
Integration_test/
├── config.py                 # Configuration settings
├── test_data_generator.py    # Test data generation utilities
├── api_client.py            # API testing client
├── ui_client.py             # UI testing client (Selenium)
├── test_integration.py      # Main integration test suite
├── run_tests.py             # Simple test runner
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── test_data/              # Generated test data files
├── test_outputs/           # Test outputs and reports
└── screenshots/            # UI test screenshots
```

## 🚀 Quick Start

### Prerequisites

1. **Docker Services Running**
   ```bash
   cd /path/to/geopulse
   docker-compose up -d
   ```

2. **Python Dependencies**
   ```bash
   cd Integration_test
   pip install -r requirements.txt
   ```

3. **Chrome Browser** (for UI testing)
   - Chrome browser must be installed
   - WebDriver will be automatically downloaded

### Running Tests

#### Option 1: Simple Runner
```bash
cd Integration_test
python run_tests.py
```

#### Option 2: Direct Execution
```bash
cd Integration_test
python test_integration.py
```

#### Option 3: Using Pytest
```bash
cd Integration_test
pytest test_integration.py -v
```

## 📊 Test Coverage

### API Tests
- ✅ Health check endpoint
- ✅ User registration
- ✅ User login and authentication
- ✅ Dashboard data access
- ✅ File upload functionality
- ✅ File processing status monitoring
- ✅ File download functionality
- ✅ File validation and format checking
- ✅ Error handling for invalid files
- ✅ Error handling for malformed data

### UI Tests
- ✅ User registration through web interface
- ✅ User login through web interface
- ✅ Dashboard accessibility and functionality
- ✅ File upload through web interface
- ✅ User logout functionality

### Data Validation
- ✅ File format validation (XLSX, CSV)
- ✅ Required column validation
- ✅ Data type validation
- ✅ File size validation
- ✅ Output format validation

## 🔧 Configuration

### Environment Variables

You can customize the test configuration using environment variables:

```bash
# Application URLs
export BASE_URL="http://localhost:3001"
export API_BASE_URL="http://localhost:8000"

# Test Configuration
export HEADLESS="true"  # Run UI tests in headless mode
export BROWSER="chrome"  # Browser for UI tests
export TIMEOUT="30"     # Request timeout in seconds

# Database Configuration (if needed)
export DB_HOST="localhost"
export DB_PORT="5433"
export DB_NAME="geopulse_db"
export DB_USER="geopulse_user"
export DB_PASSWORD="geopulse_secure_123"
```

### Test Configuration File

The `config.py` file contains all test configuration settings that can be modified:

- Application URLs and endpoints
- Test timeouts and retry settings
- File validation rules
- Expected response schemas
- Test data generation settings

## 📈 Test Reports

After running tests, you'll find:

1. **JSON Report**: `test_outputs/integration_test_report_YYYYMMDD_HHMMSS.json`
2. **Screenshots**: `screenshots/` (for failed UI tests)
3. **Console Output**: Detailed test progress and results

### Sample Report Structure

```json
{
  "start_time": "2025-08-20T15:30:00.000000",
  "end_time": "2025-08-20T15:35:00.000000",
  "tests": {
    "API Health Check": {"status": "passed", "result": true},
    "User Registration": {"status": "passed", "result": true},
    // ... more tests
  },
  "summary": {
    "total": 15,
    "passed": 15,
    "failed": 0,
    "skipped": 0
  }
}
```

## 🧪 Test Data

The framework automatically generates test data including:

- **Valid XLSX files** with geospatial data
- **Valid CSV files** with sample data
- **Invalid format files** for error testing
- **Malformed data files** for validation testing
- **Large files** for performance testing

### Sample Test Data Structure

```python
{
    'latitude': 12.9716,
    'longitude': 77.5946,
    'date': '2024-01-15',
    'temperature': 28.5,
    'humidity': 65.2,
    'rainfall': 12.3,
    'location': 'Bangalore',
    'station_id': 'ST1234',
    'value': 45.7
}
```

## 🔍 Debugging

### Common Issues

1. **Docker Services Not Running**
   ```bash
   docker-compose ps
   docker-compose logs api
   docker-compose logs ui
   ```

2. **Chrome WebDriver Issues**
   ```bash
   # Update Chrome browser
   # Clear WebDriver cache
   rm -rf ~/.cache/selenium
   ```

3. **Test Data Issues**
   ```bash
   # Regenerate test data
   python test_data_generator.py
   ```

### Verbose Logging

Enable detailed logging by modifying `config.py`:

```python
LOGGING_CONFIG = {
    "level": "DEBUG",  # Change from INFO to DEBUG
    # ... other settings
}
```

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start Docker services
        run: docker-compose up -d
      - name: Wait for services
        run: sleep 30
      - name: Install Python dependencies
        run: |
          cd Integration_test
          pip install -r requirements.txt
      - name: Run integration tests
        run: |
          cd Integration_test
          python run_tests.py
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: Integration_test/test_outputs/
```

### Docker Integration

You can also run tests inside a Docker container:

```dockerfile
FROM python:3.11-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

WORKDIR /app
COPY Integration_test/ .
RUN pip install -r requirements.txt

CMD ["python", "run_tests.py"]
```

## 📝 Adding New Tests

### Adding API Tests

1. Add new test method to `TestIntegration` class
2. Use `api_client` fixture for API interactions
3. Follow the naming convention: `test_XX_description`

### Adding UI Tests

1. Add new test method to `TestIntegration` class
2. Use `ui_client` fixture for UI interactions
3. Add corresponding methods to `UIClient` class if needed

### Adding Data Validation

1. Modify `validate_downloaded_file` method in `APIClient`
2. Add new validation rules to `config.py`
3. Update test assertions accordingly

## 🤝 Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Add proper error handling and logging
3. Include both positive and negative test cases
4. Update this README with new functionality
5. Ensure tests are idempotent and can run multiple times

## 📞 Support

For issues with the integration tests:

1. Check the test logs and screenshots
2. Verify Docker services are running correctly
3. Ensure all dependencies are installed
4. Check the configuration settings

---

**Happy Testing! 🎉**
