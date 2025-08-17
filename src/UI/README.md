# GeoPulse UI - Final Demo Version

A modern React-based user interface for the GeoPulse property analysis platform. This is the final demo version with enhanced features including Indian localization, XLSX downloads, and color-coded results.

## Features

- **User Authentication**: Secure login and registration system with Indian localization
- **Dashboard**: Comprehensive overview with metrics and file management
- **File Upload**: Drag-and-drop CSV upload with progress tracking
- **File Management**: View, search, filter, download XLSX files, and view HTML results
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Updates**: Live status updates and notifications
- **Demo Enhancements**: Color-coded significance indicators, modern UI, 2025 default dates

## Tech Stack

- **React 18**: Modern React with hooks and functional components
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API communication
- **React Dropzone**: File upload with drag-and-drop
- **React Hot Toast**: Toast notifications
- **Lucide React**: Beautiful icons
- **Date-fns**: Date manipulation utilities

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- GeoPulse API server running on `http://localhost:8000`

### Installation

1. Navigate to the UI directory:
   ```bash
   cd UI
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Project Structure

```
src/
├── components/          # Reusable UI components
│   └── Layout.js       # Main layout with navigation
├── contexts/           # React contexts
│   └── AuthContext.js  # Authentication state management
├── pages/              # Page components
│   ├── Login.js        # User login page
│   ├── Register.js     # User registration page
│   ├── Dashboard.js    # Main dashboard with metrics
│   └── FileUpload.js   # File upload interface
├── App.js              # Main app component with routing
├── index.js            # React entry point
└── index.css           # Global styles and Tailwind imports
```

## API Integration

The UI integrates with the GeoPulse API endpoints:

- **Authentication**: `/api/v1/auth/login`, `/api/v1/auth/register`
- **Dashboard**: `/api/v1/dashboard`
- **File Upload**: `/api/v1/files/upload`
- **File Download**: `/api/v1/files/{id}/download`

## User Flow

1. **Registration**: Users create an account with organization details
2. **Login**: Secure authentication with JWT tokens
3. **Dashboard**: View metrics and previously processed files
4. **File Upload**: Upload XLSX/CSV files with engagement details
5. **Processing**: Files are automatically processed on the server
6. **Download**: Download processed files from the dashboard

## Features in Detail

### Authentication
- Secure JWT-based authentication
- Automatic token refresh
- Protected routes
- Session persistence

### Dashboard
- Real-time metrics display
- File status tracking
- Search and filtering capabilities
- Sortable file lists
- Download functionality for processed files

### File Upload
- Drag-and-drop interface
- File type validation (XLSX, CSV)
- File size validation (50MB limit)
- Progress tracking
- Form validation for required fields

### Responsive Design
- Mobile-first approach
- Responsive navigation
- Adaptive layouts
- Touch-friendly interfaces

## Configuration

### API Base URL
The application is configured to proxy requests to `http://localhost:8000` in development. For production, update the proxy setting in `package.json` or configure your web server accordingly.

### Environment Variables
Create a `.env` file in the root directory for environment-specific configuration:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## Development

### Available Scripts

- `npm start`: Start development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm eject`: Eject from Create React App

### Code Style

The project uses:
- ESLint for code linting
- Prettier for code formatting
- Tailwind CSS for styling

### Adding New Features

1. Create new components in the `components/` directory
2. Add new pages in the `pages/` directory
3. Update routing in `App.js`
4. Add any new API integrations in the appropriate context or service files

## Troubleshooting

### Common Issues

1. **API Connection Errors**: Ensure the GeoPulse API server is running on port 8000
2. **CORS Issues**: The development proxy should handle CORS automatically
3. **Build Errors**: Clear node_modules and reinstall dependencies

### Debug Mode

Enable debug logging by setting the browser's localStorage:
```javascript
localStorage.setItem('debug', 'true');
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the GeoPulse platform and follows the same licensing terms.

## Support

For support and questions, please refer to the main GeoPulse documentation or contact the development team.
