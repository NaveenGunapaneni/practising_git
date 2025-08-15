# GeoPulse - Professional Data Processing Platform

A modern, responsive web application for data processing and analysis with a comprehensive React frontend and Python FastAPI backend.

## 🚀 Features

### Frontend (React)
- **Modern UI/UX**: Clean, professional interface with responsive design
- **Authentication System**: Complete login/register with JWT token management
- **Dashboard**: Real-time metrics and file management
- **File Upload**: Drag & drop CSV file upload with progress tracking
- **Notifications**: Toast notification system for user feedback
- **Protected Routes**: Secure navigation with authentication guards
- **Fallback Support**: Works with or without backend connectivity

### Backend (Python FastAPI)
- **RESTful API**: Comprehensive API endpoints
- **PostgreSQL Database**: Robust data storage
- **Authentication**: JWT-based user authentication
- **File Processing**: CSV file upload and processing
- **Health Monitoring**: API health check endpoints

## 📁 Project Structure

```
GeoPulse/
├── src/                          # React Frontend
│   ├── components/
│   │   ├── LoginPage/           # User authentication
│   │   ├── RegisterPage/        # User registration
│   │   ├── DashboardPage/       # Main dashboard
│   │   ├── UploadPage/          # File upload interface
│   │   └── common/              # Shared components
│   ├── contexts/                # React contexts
│   ├── services/                # API service layer
│   ├── utils/                   # Utility functions
│   └── config/                  # Configuration files
├── geopulse_api/                # Python FastAPI Backend
│   ├── setup_postgres.sql      # Database setup script
│   └── [API implementation]
└── public/                      # Static assets
```

## 🛠️ Installation & Setup

### Prerequisites
- Node.js (v16 or higher)
- PostgreSQL (v12 or higher)
- Python (v3.8 or higher)

### Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### Backend Setup
```bash
# Navigate to API directory
cd geopulse_api

# Install Python dependencies
pip install -r requirements.txt

# Set up PostgreSQL database
psql -U postgres -f setup_postgres.sql

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

### Database Configuration
The application uses PostgreSQL with the following default settings:
- **Database**: `geopulse_db`
- **User**: `geopulse_user`
- **Password**: `password123`
- **Port**: `5432`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development

# Database (for backend)
DATABASE_URL=postgresql://geopulse_user:password123@localhost:5432/geopulse_db
```

### API Endpoints
- **Authentication**: `/api/v1/auth/`
- **Dashboard**: `/api/v1/dashboard/`
- **File Management**: `/api/v1/files/`
- **Health Check**: `/api/v1/health/`

## 🎯 Key Features

### 1. Authentication System
- Secure JWT-based authentication
- User registration and login
- Protected routes and session management
- Automatic token refresh

### 2. Dashboard
- Real-time metrics display
- File management interface
- Search and filter functionality
- Responsive design for all devices

### 3. File Upload
- Drag & drop interface
- Progress tracking
- File validation (CSV only, max 10MB)
- Engagement name association

### 4. Notification System
- Toast notifications for all user actions
- Success, error, warning, and info types
- Auto-dismiss with configurable duration
- Queue management for multiple notifications

### 5. Fallback Support
- Works without backend connectivity
- Mock data for development/demo
- Graceful error handling
- Network timeout management

## 🔒 Security Features

- JWT token-based authentication
- Protected API endpoints
- Input validation and sanitization
- Secure token storage
- CORS configuration
- SQL injection prevention

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- Various screen sizes and orientations

## 🧪 Testing

```bash
# Run frontend tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run linting
npm run lint

# Format code
npm run format
```

## 🚀 Deployment

### Frontend Deployment
```bash
# Build production bundle
npm run build

# Deploy to your preferred hosting service
# (Netlify, Vercel, AWS S3, etc.)
```

### Backend Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production WSGI server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📊 Performance

- **Lazy Loading**: Components loaded on demand
- **Code Splitting**: Optimized bundle sizes
- **Caching**: API response caching
- **Compression**: Gzip compression enabled
- **CDN Ready**: Static assets optimized for CDN

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

- **v1.0.0**: Initial release with full authentication and dashboard
- **v1.1.0**: Added file upload functionality
- **v1.2.0**: Enhanced notification system
- **v1.3.0**: Added fallback support and improved error handling

---

**Built with ❤️ by the GeoPulse Development Team**