# 🛡️ API Usage Control System for Sentinel Hub

## 📋 Overview

This system implements comprehensive API usage control for Sentinel Hub API calls, ensuring users stay within their allocated limits and preventing abuse.

## 🗄️ Database Schema

### `user_api_usage` Table (PostgreSQL)
```sql
CREATE TABLE user_api_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    allowed_api_calls INTEGER DEFAULT 50,
    performed_api_calls INTEGER DEFAULT 0,
    user_created_date TIMESTAMP WITH TIME ZONE NOT NULL,
    user_expiry_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_api_usage_user_id 
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);
```

## 🔧 Key Features

### 1. **Automatic User Registration**
- New users automatically get 50 API calls
- Account expires 30 days from registration
- API usage record created during registration process

### 2. **Pre-Processing API Limit Check**
- Before processing any file, system checks if user has enough API calls
- Calculates required calls: `properties_count × 2` (before + after periods)
- Blocks processing if insufficient calls remaining

### 3. **Real-time Usage Tracking**
- Only successful Sentinel Hub API calls are counted
- Failed API calls don't consume user's quota
- Usage updated immediately after successful processing

### 4. **Expiry Management**
- Users can't make API calls after expiry date
- Automatic expiry checking on every API call
- Admin functions to extend expiry dates

## 🚀 Setup Instructions

### 1. Run Database Migration
```bash
python run_migration.py
```

### 2. Setup API Usage for Existing Users
```bash
python setup_api_usage.py
```

### 3. Verify Setup
The setup script will show:
- Total users with API usage records
- Sample usage information
- Verification results

## 📊 API Endpoints

### Check User's API Usage Status
```http
GET /api/v1/api-usage/status
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "user_id": 1,
    "allowed_calls": 50,
    "performed_calls": 15,
    "remaining_calls": 35,
    "usage_percentage": 30.0,
    "account_created": "2025-08-15",
    "account_expires": "2025-09-14",
    "days_until_expiry": 30,
    "is_expired": false
  }
}
```

### Check if User Can Make Specific Number of API Calls
```http
GET /api/v1/api-usage/check-limit/10
Authorization: Bearer <jwt_token>
```

### Extend User's Expiry Date (Admin)
```http
POST /api/v1/api-usage/extend-expiry/30
Authorization: Bearer <jwt_token>
```

### Reset User's API Call Counter (Admin)
```http
POST /api/v1/api-usage/reset-calls
Authorization: Bearer <jwt_token>
```

## 🔒 Access Control Logic

### API Calls Allowed When:
```
Performed_API_calls < Allowed_API_calls
AND
Today <= User_expiry_date
```

### API Calls Blocked When:
- User has reached their API call limit
- User's account has expired
- API usage record doesn't exist

## 🎯 Usage Flow

### 1. File Upload Process
```
User uploads file → Check API limits → Process if allowed → Update usage counter
```

### 2. API Limit Check
```python
required_calls = len(properties) * 2  # Before + After periods
can_make_calls, error_message, usage_info = await api_service.check_api_limit(user_id, required_calls)
```

### 3. Usage Update
```python
# Only count successful API calls
if successful_calls > 0:
    await api_service.increment_api_usage(user_id, successful_calls)
```

## 📈 Default Settings

| Setting | Value | Description |
|---------|-------|-------------|
| Default API Calls | 50 | New users get 50 API calls |
| Account Duration | 30 days | Accounts expire 30 days from creation |
| API Calls per Property | 2 | Before period + After period |

## 🛠️ Administration

### View All Users' Usage
```python
api_service = APIUsageService(db)
all_usage = await api_service.get_all_users_usage()
```

### Extend User's Account
```python
success = await api_service.extend_user_expiry(user_id, days=30)
```

### Reset User's API Calls
```python
success = await api_service.reset_user_api_calls(user_id, new_limit=100)
```

## 🔍 Monitoring & Logging

### API Usage Logs
- Every API limit check is logged
- Successful/failed API calls tracked
- Usage updates logged with before/after counts
- Expiry warnings logged

### Error Messages
- **Limit Exceeded**: "API call limit exceeded. Used: X/Y. Need Z more calls."
- **Account Expired**: "User account expired on YYYY-MM-DD. Please renew your subscription."
- **No Record**: "API usage record not found. Please contact support."

## 🚨 Error Handling

### File Processing Errors
- If API limit exceeded: Processing stops immediately
- Clear error message returned to user
- No partial processing or misleading results

### Database Errors
- Rollback on failed usage updates
- Graceful error handling with user-friendly messages
- Comprehensive logging for debugging

## 🎉 Benefits

1. **Cost Control**: Prevents unlimited API usage
2. **Fair Usage**: Ensures equitable access for all users
3. **Transparency**: Users can check their usage anytime
4. **Flexibility**: Admin controls for extending/resetting limits
5. **Accuracy**: Only successful API calls counted
6. **Security**: Prevents API abuse and unauthorized usage

## 📝 Future Enhancements

- Usage analytics and reporting
- Different pricing tiers with different limits
- Automatic account renewal
- Usage alerts and notifications
- Bulk user management tools