# GeoPulse API Testing

## Quick Setup

1. **Import into Postman**:
   - Import `GeoPulse-Complete-API-Tests.postman_collection.json`
   - Import `GeoPulse-Environment.postman_environment.json`
   - Select "GeoPulse Environment"

2. **Start GeoPulse Application**:
   ```bash
   cd geopulse
   python main.py
   ```

## Collection Structure

```
GeoPulse Complete API Tests
├── User Registration API
│   ├── Success Cases
│   │   └── Register New User Successfully
│   └── Failure Cases
│       └── Duplicate Email Registration
├── User Authentication API
│   ├── Success Cases
│   │   └── Login User Successfully
│   └── Failure Cases
│       └── Invalid Password Login
├── Dashboard Data API
│   ├── Success Cases
│   │   ├── Get Dashboard Data
│   │   └── Dashboard with Pagination
│   └── Failure Cases
│       └── Unauthorized Dashboard Access
└── File Upload Processing API
    ├── Success Cases
    │   ├── Upload File Successfully
    │   ├── Get File Status
    │   └── Get User Files List
    └── Failure Cases
        └── Unauthorized File Upload
```

## Test Sequence

Run tests in this order for automatic variable population:

1. **User Registration API** → Register New User Successfully
2. **User Authentication API** → Login User Successfully  
3. **Dashboard Data API** → Get Dashboard Data
4. **File Upload Processing API** → Upload File Successfully

## Environment Variables

- `base_url` - GeoPulse API base URL
- `unique_email` - Auto-generated unique email
- `auth_token` - JWT token from login
- `user_id` - User ID from registration
- `file_id` - File ID from upload

## Files Required

Ensure `sample_properties_for_geopulse.csv` exists in your project root for file upload tests.

## Expected Results

- ✅ Success cases: 200/201 status codes
- ❌ Failure cases: 400/401 status codes
- 🔄 Variables auto-populate between tests