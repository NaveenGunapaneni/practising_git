# GeoPulse API Integration

This document outlines the comprehensive API integration implemented for the GeoPulse React frontend.

## Overview

The frontend now includes a complete API service layer that communicates with the Python FastAPI backend located in the `geopulse_api` folder.

## Architecture

### 1. API Service Layer (`src/services/api.js`)
- Centralized HTTP client with error handling
- Authentication token management
- Request/response interceptors
- Timeout and retry logic

### 2. Authentication Context (`src/contexts/AuthContext.js`)
- User authentication state management
- Login/register/logout functionality
- Token persistence and validation
- Protected route handling

### 3. Error Handling (`src/utils/errorHandler.js`)
- Standardized error processing
- User-friendly error messages
- API error parsing and formatting

### 4. Notification System (`src/components/common/NotificationSystem.jsx`)
- Toast notifications for user feedback
- Success, error, warning, and info types
- Auto-dismiss functionality
- Queue management for multiple notifications

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Dashboard
- `GET /dashboard` - Get dashboard data including metrics and recent files

### File Management
- `POST /files/upload` - Upload CSV files
- `GET /files` - List user files
- `GET /files/{file_id}` - Get specific file details
- `DELETE /files/{file_id}` - Delete file

### Health Check
- `GET /health` - API health status

## Components Updated

### LoginPage
- Integrated with authentication API
- Form validation and error handling
- Automatic redirect on successful login

### RegisterPage
- User registration with API integration
- Real-time password validation
- Success notifications and redirect

### DashboardPage
- Fetches real dashboard data from API
- User info display from authentication context
- Proper logout handling

### UploadPage (New)
- File upload with progress tracking
- Drag and drop functionality
- File validation and error handling

## Configuration

### Environment Settings (`src/config/environment.js`)
- Development: `http://localhost:8000`
- Production: Configurable via `REACT_APP_API_URL`

### Protected Routes
- Dashboard and Upload pages require authentication
- Automatic redirect to login for unauthenticated users
- Loading states during authentication checks

## Usage

1. **Start the backend API server** (from `geopulse_api` folder)
2. **Start the React development server**: `npm start`
3. **Register a new account** or login with existing credentials
4. **Access the dashboard** to view metrics and files
5. **Upload files** using the upload page

## Error Handling

The system includes comprehensive error handling:
- Network errors with retry logic
- Authentication errors with automatic logout
- Validation errors with field-specific messages
- Server errors with user-friendly notifications

## Security Features

- JWT token-based authentication
- Automatic token refresh handling
- Secure token storage
- Protected API endpoints
- Input validation and sanitization

## Next Steps

1. Implement file processing status updates
2. Add real-time notifications for file processing
3. Implement file download functionality
4. Add user profile management
5. Implement advanced filtering and search