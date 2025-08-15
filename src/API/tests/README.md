# Tests Directory

This directory contains unit tests for the GeoPulse API application. Tests ensure code quality, catch regressions, and validate functionality across different components.

## Test Files

### `test_password_service.py`
**Purpose**: Tests for password security operations

**Test Coverage**:
- Password hashing functionality
- Password verification
- Password strength validation
- Error handling for invalid inputs
- Security edge cases

### `test_file_service.py`
**Purpose**: Tests for file system operations

**Test Coverage**:
- JSON file creation
- Directory access validation
- Path security validation
- File system error handling
- Logo path validation

### `test_user_repository.py`
**Purpose**: Tests for database operations

**Test Coverage**:
- User creation in database
- User retrieval operations
- Email uniqueness validation
- Database transaction handling
- Error scenarios

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_password_service.py
```

### Run with Coverage
```bash
pytest --cov=app
```

### Run with Verbose Output
```bash
pytest -v
```

## Test Structure

### Test Organization
Tests are organized by the component they test:
- Service tests validate business logic
- Repository tests validate data access
- Integration tests validate end-to-end workflows

### Test Patterns
```python
def test_function_name():
    # Arrange - Set up test data
    # Act - Execute the function
    # Assert - Verify the results
```

### Async Testing
For async functions:
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

## Test Dependencies

### Required Packages
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for API testing

### Test Database
Tests should use a separate test database or in-memory SQLite to avoid affecting development data.

## Best Practices

### Test Isolation
- Each test should be independent
- Use fixtures for common setup
- Clean up after tests

### Mock External Dependencies
- Mock database calls when testing business logic
- Mock file system operations
- Mock external API calls

### Test Coverage Goals
- Aim for 80%+ code coverage
- Focus on critical business logic
- Test error scenarios and edge cases

### Naming Conventions
- Test files: `test_*.py`
- Test functions: `test_*`
- Descriptive test names that explain what is being tested

## Adding New Tests

When adding new functionality:

1. **Write tests first** (TDD approach)
2. **Test happy path** - Normal successful operations
3. **Test error cases** - Invalid inputs, failures
4. **Test edge cases** - Boundary conditions
5. **Test security** - Validation, sanitization

### Example Test Structure
```python
class TestUserService:
    def test_register_user_success(self):
        # Test successful user registration
        pass
    
    def test_register_user_duplicate_email(self):
        # Test duplicate email handling
        pass
    
    def test_register_user_invalid_data(self):
        # Test validation error handling
        pass
```

This comprehensive test suite ensures the reliability and security of the GeoPulse API.