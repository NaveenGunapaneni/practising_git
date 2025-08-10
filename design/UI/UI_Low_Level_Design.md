# UI Low-Level Design Document
## GeoPulse Web Application

**Document Version:** 1.0  
**Date:** August 2025  
**Project:** GeoPulse  
**Document Type:** UI Low-Level Design  

---

## Table of Contents
1. [Technology Stack](#technology-stack)
2. [Project Structure](#project-structure)
3. [Component Architecture](#component-architecture)
4. [Page-by-Page Design](#page-by-page-design)
5. [Component Specifications](#component-specifications)
6. [State Management](#state-management)
7. [Routing Configuration](#routing-configuration)
8. [Styling Guidelines](#styling-guidelines)
9. [Responsive Design](#responsive-design)
10. [Error Handling](#error-handling)
11. [Performance Optimization](#performance-optimization)
12. [Development Setup](#development-setup)

---

## Technology Stack

### Frontend Technologies
- **Framework:** React.js 18.x
- **Language:** JavaScript/TypeScript
- **Styling:** CSS3 with CSS Modules
- **Build Tool:** Vite
- **Package Manager:** npm/yarn
- **HTTP Client:** Axios
- **State Management:** React Context API + useState/useReducer
- **Routing:** React Router v6
- **Form Handling:** React Hook Form
- **Validation:** Yup
- **File Upload:** React Dropzone

### Development Tools
- **Code Editor:** VS Code
- **Browser DevTools:** Chrome DevTools
- **Version Control:** Git
- **Package Manager:** npm

---

## Project Structure

```
src/
├── components/
│   ├── common/
│   │   ├── Header.jsx
│   │   ├── Footer.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── ErrorBoundary.jsx
│   │   ├── Modal.jsx
│   │   └── Button.jsx
│   ├── auth/
│   │   ├── LoginForm.jsx
│   │   └── RegisterForm.jsx
│   ├── dashboard/
│   │   ├── Dashboard.jsx
│   │   ├── FileUpload.jsx
│   │   ├── TransactionHistory.jsx
│   │   └── Metrics.jsx
│   └── layout/
│       ├── MainLayout.jsx
│       └── Sidebar.jsx
├── pages/
│   ├── Login.jsx
│   ├── Register.jsx
│   ├── Dashboard.jsx
│   ├── FileUpload.jsx
│   ├── TransactionHistory.jsx
│   ├── Profile.jsx
│   └── Error404.jsx
├── hooks/
│   ├── useAuth.js
│   ├── useApi.js
│   └── useFileUpload.js
├── services/
│   ├── api.js
│   ├── authService.js
│   └── fileService.js
├── utils/
│   ├── constants.js
│   ├── helpers.js
│   └── validation.js
├── styles/
│   ├── global.css
│   ├── variables.css
│   └── components/
├── context/
│   └── AuthContext.jsx
└── App.jsx
```

---

## Component Architecture

### 1. Common Components

#### Header Component (`components/common/Header.jsx`)
```jsx
// Purpose: Main navigation header with logo and user menu
// Props: user (object), onLogout (function)
// State: isMenuOpen (boolean)

import React, { useState } from 'react';
import './Header.css';

const Header = ({ user, onLogout }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="header">
      <div className="header-logo">
        <img src={user?.logo || '/default-logo.png'} alt="Company Logo" />
      </div>
      <nav className="header-nav">
        <ul className="nav-tabs">
          <li><a href="/upload">New Upload</a></li>
          <li><a href="/history">Past Uploads</a></li>
          <li><a href="/profile">Profile</a></li>
          <li><a href="/usage">Usage & Limits</a></li>
          <li><a href="/messages">Messages</a></li>
        </ul>
      </nav>
      <div className="header-user">
        <span>{user?.userName}</span>
        <button onClick={onLogout}>Logout</button>
      </div>
    </header>
  );
};

export default Header;
```

#### LoadingSpinner Component (`components/common/LoadingSpinner.jsx`)
```jsx
// Purpose: Reusable loading indicator
// Props: size (string), message (string)

import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ size = 'medium', message = 'Loading...' }) => {
  return (
    <div className={`loading-spinner ${size}`}>
      <div className="spinner"></div>
      <p className="loading-message">{message}</p>
    </div>
  );
};

export default LoadingSpinner;
```

### 2. Authentication Components

#### LoginForm Component (`components/auth/LoginForm.jsx`)
```jsx
// Purpose: User login form with validation
// Props: onSubmit (function), isLoading (boolean)
// State: formData (object), errors (object)

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import './LoginForm.css';

const schema = yup.object({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(6, 'Password must be at least 6 characters').required('Password is required')
});

const LoginForm = ({ onSubmit, isLoading }) => {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema)
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="login-form">
      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          type="email"
          id="email"
          {...register('email')}
          className={errors.email ? 'error' : ''}
        />
        {errors.email && <span className="error-message">{errors.email.message}</span>}
      </div>
      
      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          {...register('password')}
          className={errors.password ? 'error' : ''}
        />
        {errors.password && <span className="error-message">{errors.password.message}</span>}
      </div>
      
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};

export default LoginForm;
```

### 3. Dashboard Components

#### FileUpload Component (`components/dashboard/FileUpload.jsx`)
```jsx
// Purpose: File upload interface with drag-and-drop
// Props: onUpload (function), isLoading (boolean)
// State: selectedFile (object), engagementName (string), dates (array)

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import DatePicker from 'react-datepicker';
import './FileUpload.css';

const FileUpload = ({ onUpload, isLoading }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [engagementName, setEngagementName] = useState('');
  const [dates, setDates] = useState([null, null, null, null]);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file && (file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                 file.type === 'text/csv')) {
      setSelectedFile(file);
    } else {
      alert('Please select only XLSX or CSV files');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv']
    },
    multiple: false
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile || !engagementName || dates.some(date => !date)) {
      alert('Please fill all required fields');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('engagementName', engagementName);
    dates.forEach((date, index) => {
      formData.append(`date${index + 1}`, date.toISOString().split('T')[0]);
    });
    
    onUpload(formData);
  };

  return (
    <div className="file-upload">
      <h2>Upload New File</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="upload-area" {...getRootProps()}>
          <input {...getInputProps()} />
          {isDragActive ? (
            <p>Drop the file here...</p>
          ) : (
            <p>Drag and drop a file here, or click to select</p>
          )}
          {selectedFile && (
            <p className="selected-file">Selected: {selectedFile.name}</p>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="engagementName">Engagement Name *</label>
          <input
            type="text"
            id="engagementName"
            value={engagementName}
            onChange={(e) => setEngagementName(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label>Select 4 Dates *</label>
          <div className="date-pickers">
            {dates.map((date, index) => (
              <DatePicker
                key={index}
                selected={date}
                onChange={(date) => {
                  const newDates = [...dates];
                  newDates[index] = date;
                  setDates(newDates);
                }}
                dateFormat="yyyy-MM-dd"
                placeholderText={`Date ${index + 1}`}
                required
              />
            ))}
          </div>
        </div>

        <button type="submit" disabled={isLoading || !selectedFile}>
          {isLoading ? 'Uploading...' : 'Submit'}
        </button>
      </form>
    </div>
  );
};

export default FileUpload;
```

---

## Page-by-Page Design

### 1. Login Page (`pages/Login.jsx`)
```jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';
import { loginUser } from '../services/authService';
import './Login.css';

const Login = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (formData) => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await loginUser(formData);
      localStorage.setItem('token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>Welcome to GeoPulse</h1>
          <p>Please login to continue</p>
        </div>
        
        {error && <div className="error-alert">{error}</div>}
        
        <LoginForm onSubmit={handleLogin} isLoading={isLoading} />
        
        <div className="login-footer">
          <p>Don't have an account? <a href="/register">Register here</a></p>
        </div>
      </div>
    </div>
  );
};

export default Login;
```

### 2. Dashboard Page (`pages/Dashboard.jsx`)
```jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/common/Header';
import FileUpload from '../components/dashboard/FileUpload';
import TransactionHistory from '../components/dashboard/TransactionHistory';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { getDashboardData } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import './Dashboard.css';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    loadDashboardData();
  }, [user, navigate]);

  const loadDashboardData = async () => {
    try {
      const data = await getDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  return (
    <div className="dashboard">
      <Header user={user} onLogout={handleLogout} />
      
      <div className="dashboard-content">
        <div className="dashboard-tabs">
          <button 
            className={activeTab === 'upload' ? 'active' : ''}
            onClick={() => setActiveTab('upload')}
          >
            New Upload
          </button>
          <button 
            className={activeTab === 'history' ? 'active' : ''}
            onClick={() => setActiveTab('history')}
          >
            Past Uploads
          </button>
        </div>
        
        <div className="dashboard-main">
          {activeTab === 'upload' && (
            <FileUpload onUpload={handleFileUpload} />
          )}
          {activeTab === 'history' && (
            <TransactionHistory data={dashboardData?.transactions} />
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
```

---

## State Management

### AuthContext (`context/AuthContext.jsx`)
```jsx
import React, { createContext, useContext, useReducer, useEffect } from 'react';

const AuthContext = createContext();

const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true
};

const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload
      };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    // Check for existing token on app load
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (token && user) {
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { token, user }
      });
    } else {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  const login = (userData) => {
    dispatch({
      type: 'LOGIN_SUCCESS',
      payload: userData
    });
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    dispatch({ type: 'LOGOUT' });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

---

## Routing Configuration

### App.jsx with Routes
```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/common/PrivateRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Error404 from './pages/Error404';
import './App.css';

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route 
              path="/dashboard" 
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              } 
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Error404 />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
```

---

## Styling Guidelines

### Global CSS Variables (`styles/variables.css`)
```css
:root {
  /* Colors */
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  --background-color: #f8fafc;
  --surface-color: #ffffff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;

  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;

  /* Border Radius */
  --border-radius-sm: 0.25rem;
  --border-radius-md: 0.375rem;
  --border-radius-lg: 0.5rem;
  --border-radius-xl: 0.75rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}
```

### Component CSS Example (`components/auth/LoginForm.css`)
```css
.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: var(--spacing-xl);
  background: var(--surface-color);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.form-group input {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  transition: border-color 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgb(37 99 235 / 0.1);
}

.form-group input.error {
  border-color: var(--error-color);
}

.error-message {
  color: var(--error-color);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-xs);
}

.login-form button {
  width: 100%;
  padding: var(--spacing-md);
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.login-form button:hover:not(:disabled) {
  background: #1d4ed8;
}

.login-form button:disabled {
  background: var(--secondary-color);
  cursor: not-allowed;
}
```

---

## Development Setup

### 1. Project Initialization
```bash
# Create new React project with Vite
npm create vite@latest geopulse-ui -- --template react

# Navigate to project directory
cd geopulse-ui

# Install dependencies
npm install

# Install additional required packages
npm install react-router-dom axios react-hook-form @hookform/resolvers yup react-dropzone react-datepicker
```

### 2. Package.json Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0",
    "react-hook-form": "^7.43.0",
    "@hookform/resolvers": "^2.9.0",
    "yup": "^1.0.0",
    "react-dropzone": "^14.2.0",
    "react-datepicker": "^4.8.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.27",
    "@types/react-dom": "^18.0.10",
    "@vitejs/plugin-react": "^3.1.0",
    "vite": "^4.1.0"
  }
}
```

### 3. Development Commands
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
```

### 4. Environment Configuration
Create `.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=GeoPulse
```

---

## Error Handling

### Error Boundary Component
```jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>Please refresh the page or contact support</p>
          <button onClick={() => window.location.reload()}>
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

---

## Performance Optimization

### 1. Code Splitting
```jsx
import React, { lazy, Suspense } from 'react';
import LoadingSpinner from './components/common/LoadingSpinner';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const FileUpload = lazy(() => import('./pages/FileUpload'));

// Wrap lazy components with Suspense
<Suspense fallback={<LoadingSpinner />}>
  <Dashboard />
</Suspense>
```

### 2. Memoization
```jsx
import React, { memo, useMemo, useCallback } from 'react';

const ExpensiveComponent = memo(({ data, onAction }) => {
  const processedData = useMemo(() => {
    return data.map(item => ({ ...item, processed: true }));
  }, [data]);

  const handleClick = useCallback(() => {
    onAction(processedData);
  }, [processedData, onAction]);

  return (
    <div onClick={handleClick}>
      {/* Component content */}
    </div>
  );
});
```

---

## Testing Setup

### 1. Unit Testing with Jest and React Testing Library
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest
```

### 2. Test Example
```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from '../LoginForm';

test('renders login form', () => {
  render(<LoginForm onSubmit={jest.fn()} />);
  
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
});

test('shows validation errors', async () => {
  render(<LoginForm onSubmit={jest.fn()} />);
  
  const submitButton = screen.getByRole('button', { name: /login/i });
  fireEvent.click(submitButton);
  
  expect(await screen.findByText(/email is required/i)).toBeInTheDocument();
});
```

---

## Deployment

### 1. Build Process
```bash
# Build the application
npm run build

# The build output will be in the 'dist' folder
```

### 2. Production Deployment
- Upload the contents of the `dist` folder to your web server
- Configure your web server to serve `index.html` for all routes (for React Router)
- Set up environment variables for production API endpoints

---

## Next Steps for Developers

1. **Start with the Login page** - Implement basic authentication flow
2. **Create reusable components** - Build common components first
3. **Implement routing** - Set up navigation between pages
4. **Add state management** - Implement AuthContext for user management
5. **Build file upload functionality** - Implement drag-and-drop file upload
6. **Add error handling** - Implement proper error boundaries and user feedback
7. **Style your components** - Apply CSS and make it responsive
8. **Test thoroughly** - Write unit tests for all components
9. **Optimize performance** - Implement code splitting and memoization
10. **Deploy and monitor** - Deploy to production and monitor for issues

Remember to:
- Follow the component structure exactly as specified
- Use the provided CSS variables for consistent styling
- Implement proper error handling in all components
- Write tests for all functionality
- Keep components small and focused on single responsibilities
- Use TypeScript for better type safety (optional but recommended)
