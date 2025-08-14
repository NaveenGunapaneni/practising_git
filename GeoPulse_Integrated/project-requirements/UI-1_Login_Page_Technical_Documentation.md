# UI-1: Login Page - Technical Documentation
## GeoPulse Web Application

**Component:** Login Page  
**Date:** August 2025  
**Version:** 1.0  
**Framework:** React.js 18.x  

---

## Table of Contents
1. [Wireframe Diagrams](#wireframe-diagrams)
2. [Test API Setup](#test-api-setup)
3. [Testing Tips](#testing-tips)
4. [UX Styling Guidelines](#ux-styling-guidelines)

---

## Wireframe Diagrams

### Desktop Layout (1200px+)
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    [Company Logo]                              │
│                                                                 │
│              ┌─────────────────────────────────┐              │
│              │                                 │              │
│              │        Welcome to GeoPulse      │              │
│              │                                 │              │
│              │      Please login to continue   │              │
│              │                                 │              │
│              │  ┌─────────────────────────────┐ │              │
│              │  │ Email Address              │ │              │
│              │  │ [________________________] │ │              │
│              │  │                             │ │              │
│              │  │ Password                    │ │              │
│              │  │ [________________________] │ │              │
│              │  │ [👁] Show/Hide Password     │ │              │
│              │  │                             │ │              │
│              │  │ [✓] Remember me             │ │              │
│              │  │                             │ │              │
│              │  │ [     Login Button     ]    │ │              │
│              │  │                             │ │              │
│              │  │ Forgot Password? [Link]     │ │              │
│              │  │                             │ │              │
│              │  │ Don't have an account?      │ │              │
│              │  │ [Register here]             │ │              │
│              │  └─────────────────────────────┘ │              │
│              │                                 │              │
│              └─────────────────────────────────┘              │
│                                                                 │
│              [Footer: © 2025 GeoPulse. All rights reserved.]   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Tablet Layout (768px - 1199px)
```
┌─────────────────────────────────────────────────┐
│                                                 │
│              [Company Logo]                     │
│                                                 │
│        ┌─────────────────────────────────┐      │
│        │                                 │      │
│        │        Welcome to GeoPulse      │      │
│        │                                 │      │
│        │      Please login to continue   │      │
│        │                                 │      │
│        │  ┌─────────────────────────────┐ │      │
│        │  │ Email Address              │ │      │
│        │  │ [________________________] │ │      │
│        │  │                             │ │      │
│        │  │ Password                    │ │      │
│        │  │ [________________________] │ │      │
│        │  │ [👁] Show/Hide Password     │ │      │
│        │  │                             │ │      │
│        │  │ [✓] Remember me             │ │      │
│        │  │                             │ │      │
│        │  │ [     Login Button     ]    │ │      │
│        │  │                             │ │      │
│        │  │ Forgot Password? [Link]     │ │      │
│        │  │                             │ │      │
│        │  │ Don't have an account?      │ │      │
│        │  │ [Register here]             │ │      │
│        │  └─────────────────────────────┘ │      │
│        │                                 │      │
│        └─────────────────────────────────┘      │
│                                                 │
│        [Footer: © 2025 GeoPulse]                │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Mobile Layout (320px - 767px)
```
┌─────────────────────────────────┐
│                                 │
│        [Company Logo]           │
│                                 │
│ ┌─────────────────────────────┐ │
│ │                             │ │
│ │      Welcome to GeoPulse    │ │
│ │                             │ │
│ │    Please login to continue │ │
│ │                             │ │
│ │ ┌─────────────────────────┐ │ │
│ │ │ Email Address          │ │ │
│ │ │ [_____________________] │ │ │
│ │ │                         │ │ │
│ │ │ Password                │ │ │
│ │ │ [_____________________] │ │ │
│ │ │ [👁] Show/Hide Password │ │ │
│ │ │                         │ │ │
│ │ │ [✓] Remember me         │ │ │
│ │ │                         │ │ │
│ │ │ [   Login Button   ]    │ │ │
│ │ │                         │ │ │
│ │ │ Forgot Password? [Link] │ │ │
│ │ │                         │ │ │
│ │ │ Don't have an account?  │ │ │
│ │ │ [Register here]         │ │ │
│ │ └─────────────────────────┘ │ │
│ │                             │ │
│ └─────────────────────────────┘ │
│                                 │
│ [Footer: © 2025 GeoPulse]       │
│                                 │
└─────────────────────────────────┘
```

### Component Hierarchy
```
LoginPage
├── Header
│   └── Logo
├── MainContent
│   ├── WelcomeSection
│   │   ├── Title
│   │   └── Subtitle
│   └── LoginForm
│       ├── EmailInput
│       ├── PasswordInput
│       ├── ShowPasswordToggle
│       ├── RememberMeCheckbox
│       ├── LoginButton
│       ├── ForgotPasswordLink
│       └── RegisterLink
└── Footer
    └── Copyright
```

---

## Test API Setup

### 1. Create Mock API Server

#### Using JSON Server
```bash
# Install JSON Server
npm install -g json-server

# Create db.json file
```

```json
// db.json
{
  "users": [
    {
      "id": 1,
      "email": "john.doe@acmecorp.com",
      "password": "hashed_password_123",
      "user_name": "John Doe",
      "organization_name": "Acme Corporation"
    },
    {
      "id": 2,
      "email": "jane.smith@demoinc.com",
      "password": "hashed_password_456",
      "user_name": "Jane Smith",
      "organization_name": "Demo Inc"
    }
  ],
  "auth": {
    "tokens": []
  }
}
```

```bash
# Start JSON Server
json-server --watch db.json --port 3001
```

#### Using Express.js Mock Server
```javascript
// mock-server.js
const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const app = express();
app.use(cors());
app.use(express.json());

// Mock users database
const users = [
  {
    id: 1,
    email: 'john.doe@acmecorp.com',
    password: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', // "password123"
    user_name: 'John Doe',
    organization_name: 'Acme Corporation'
  }
];

// Login endpoint
app.post('/api/v1/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    // Find user
    const user = users.find(u => u.email === username);
    if (!user) {
      return res.status(401).json({
        status: 'error',
        error_code: 'E004',
        message: 'Invalid credentials',
        timestamp: new Date().toISOString()
      });
    }
    
    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({
        status: 'error',
        error_code: 'E004',
        message: 'Invalid credentials',
        timestamp: new Date().toISOString()
      });
    }
    
    // Generate JWT token
    const token = jwt.sign(
      { sub: user.id, email: user.email },
      'your-secret-key',
      { expiresIn: '30m' }
    );
    
    res.json({
      status: 'success',
      data: {
        access_token: token,
        token_type: 'bearer',
        expires_in: 1800,
        user: {
          user_id: user.id,
          user_name: user.user_name,
          email: user.email,
          organization_name: user.organization_name
        }
      },
      message: 'Login successful',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    res.status(500).json({
      status: 'error',
      error_code: 'E003',
      message: 'Internal server error',
      timestamp: new Date().toISOString()
    });
  }
});

app.listen(3001, () => {
  console.log('Mock API server running on http://localhost:3001');
});
```

### 2. Environment Configuration
```javascript
// .env.development
REACT_APP_API_BASE_URL=http://localhost:3001
REACT_APP_USE_MOCK_API=true
REACT_APP_MOCK_DELAY=1000

// .env.production
REACT_APP_API_BASE_URL=https://api.geopulse.com
REACT_APP_USE_MOCK_API=false
```

### 3. API Service Configuration
```javascript
// services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
const USE_MOCK_API = process.env.REACT_APP_USE_MOCK_API === 'true';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for mock delay
if (USE_MOCK_API) {
  api.interceptors.request.use(async (config) => {
    const delay = parseInt(process.env.REACT_APP_MOCK_DELAY) || 1000;
    await new Promise(resolve => setTimeout(resolve, delay));
    return config;
  });
}

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;
```

### 4. Test Data Setup
```javascript
// test-data/login-test-data.js
export const testUsers = [
  {
    email: 'john.doe@acmecorp.com',
    password: 'password123',
    user_name: 'John Doe',
    organization_name: 'Acme Corporation'
  },
  {
    email: 'jane.smith@demoinc.com',
    password: 'password456',
    user_name: 'Jane Smith',
    organization_name: 'Demo Inc'
  },
  {
    email: 'invalid@test.com',
    password: 'wrongpassword',
    user_name: 'Invalid User',
    organization_name: 'Test Corp'
  }
];

export const testScenarios = [
  {
    name: 'Valid Login',
    email: 'john.doe@acmecorp.com',
    password: 'password123',
    expectedResult: 'success'
  },
  {
    name: 'Invalid Email',
    email: 'nonexistent@test.com',
    password: 'password123',
    expectedResult: 'error'
  },
  {
    name: 'Invalid Password',
    email: 'john.doe@acmecorp.com',
    password: 'wrongpassword',
    expectedResult: 'error'
  },
  {
    name: 'Empty Fields',
    email: '',
    password: '',
    expectedResult: 'validation_error'
  }
];
```

---

## Testing Tips

### 1. Unit Testing with Jest and React Testing Library
```javascript
// LoginPage.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../LoginPage';

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('LoginPage', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  test('renders login form with all required elements', () => {
    renderWithRouter(<LoginPage />);
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    expect(screen.getByText(/welcome to geopulse/i)).toBeInTheDocument();
  });

  test('shows validation errors for empty fields', async () => {
    renderWithRouter(<LoginPage />);
    
    const loginButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(loginButton);
    
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  test('shows validation error for invalid email format', async () => {
    renderWithRouter(<LoginPage />);
    
    const emailInput = screen.getByLabelText(/email/i);
    await userEvent.type(emailInput, 'invalid-email');
    
    const loginButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(loginButton);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid email format/i)).toBeInTheDocument();
    });
  });

  test('toggles password visibility', async () => {
    renderWithRouter(<LoginPage />);
    
    const passwordInput = screen.getByLabelText(/password/i);
    const toggleButton = screen.getByRole('button', { name: /show password/i });
    
    // Password should be hidden by default
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click toggle button
    fireEvent.click(toggleButton);
    
    // Password should be visible
    expect(passwordInput).toHaveAttribute('type', 'text');
    expect(screen.getByRole('button', { name: /hide password/i })).toBeInTheDocument();
  });

  test('handles successful login', async () => {
    // Mock successful API response
    const mockApiResponse = {
      status: 'success',
      data: {
        access_token: 'mock-token',
        token_type: 'bearer',
        user: {
          user_id: 1,
          user_name: 'John Doe',
          email: 'john@test.com'
        }
      }
    };
    
    // Mock the API call
    jest.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockApiResponse,
    });
    
    renderWithRouter(<LoginPage />);
    
    // Fill in form
    await userEvent.type(screen.getByLabelText(/email/i), 'john@test.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    
    // Submit form
    const loginButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(loginButton);
    
    // Wait for navigation
    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('mock-token');
    });
  });

  test('handles login error', async () => {
    // Mock error API response
    const mockErrorResponse = {
      status: 'error',
      error_code: 'E004',
      message: 'Invalid credentials'
    };
    
    // Mock the API call
    jest.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => mockErrorResponse,
    });
    
    renderWithRouter(<LoginPage />);
    
    // Fill in form
    await userEvent.type(screen.getByLabelText(/email/i), 'invalid@test.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'wrongpassword');
    
    // Submit form
    const loginButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(loginButton);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  test('disables login button during submission', async () => {
    // Mock slow API response
    jest.spyOn(global, 'fetch').mockImplementationOnce(() => 
      new Promise(resolve => setTimeout(resolve, 1000))
    );
    
    renderWithRouter(<LoginPage />);
    
    // Fill in form
    await userEvent.type(screen.getByLabelText(/email/i), 'john@test.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    
    // Submit form
    const loginButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(loginButton);
    
    // Button should be disabled
    expect(loginButton).toBeDisabled();
    expect(loginButton).toHaveTextContent(/logging in/i);
  });
});
```

### 2. Integration Testing
```javascript
// LoginPage.integration.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../LoginPage';

// Mock the entire API module
jest.mock('../services/api', () => ({
  loginUser: jest.fn()
}));

import { loginUser } from '../services/api';

describe('LoginPage Integration Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  test('complete login flow with API integration', async () => {
    const mockLoginResponse = {
      status: 'success',
      data: {
        access_token: 'test-token-123',
        token_type: 'bearer',
        user: {
          user_id: 1,
          user_name: 'John Doe',
          email: 'john@test.com'
        }
      }
    };
    
    loginUser.mockResolvedValueOnce(mockLoginResponse);
    
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    // Fill form
    await userEvent.type(screen.getByLabelText(/email/i), 'john@test.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    
    // Submit
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    // Verify API call
    await waitFor(() => {
      expect(loginUser).toHaveBeenCalledWith({
        username: 'john@test.com',
        password: 'password123'
      });
    });
    
    // Verify token storage
    expect(localStorage.getItem('token')).toBe('test-token-123');
  });
});
```

### 3. E2E Testing with Cypress
```javascript
// cypress/e2e/login.cy.js
describe('Login Page E2E Tests', () => {
  beforeEach(() => {
    // Visit login page before each test
    cy.visit('/login');
    
    // Clear localStorage
    cy.clearLocalStorage();
  });

  it('should display login form correctly', () => {
    // Check form elements
    cy.get('[data-testid="email-input"]').should('be.visible');
    cy.get('[data-testid="password-input"]').should('be.visible');
    cy.get('[data-testid="login-button"]').should('be.visible');
    cy.get('[data-testid="show-password-toggle"]').should('be.visible');
    
    // Check welcome message
    cy.contains('Welcome to GeoPulse').should('be.visible');
    cy.contains('Please login to continue').should('be.visible');
  });

  it('should show validation errors for empty form', () => {
    // Click login without filling form
    cy.get('[data-testid="login-button"]').click();
    
    // Check validation messages
    cy.contains('Email is required').should('be.visible');
    cy.contains('Password is required').should('be.visible');
  });

  it('should show validation error for invalid email', () => {
    // Type invalid email
    cy.get('[data-testid="email-input"]').type('invalid-email');
    cy.get('[data-testid="password-input"]').type('password123');
    
    // Submit form
    cy.get('[data-testid="login-button"]').click();
    
    // Check validation message
    cy.contains('Invalid email format').should('be.visible');
  });

  it('should toggle password visibility', () => {
    // Password should be hidden by default
    cy.get('[data-testid="password-input"]').should('have.attr', 'type', 'password');
    
    // Click show password toggle
    cy.get('[data-testid="show-password-toggle"]').click();
    
    // Password should be visible
    cy.get('[data-testid="password-input"]').should('have.attr', 'type', 'text');
    
    // Click hide password toggle
    cy.get('[data-testid="show-password-toggle"]').click();
    
    // Password should be hidden again
    cy.get('[data-testid="password-input"]').should('have.attr', 'type', 'password');
  });

  it('should handle successful login', () => {
    // Mock successful API response
    cy.intercept('POST', '/api/v1/auth/login', {
      statusCode: 200,
      body: {
        status: 'success',
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
          user: {
            user_id: 1,
            user_name: 'John Doe',
            email: 'john@test.com'
          }
        }
      }
    }).as('loginRequest');
    
    // Fill form with valid credentials
    cy.get('[data-testid="email-input"]').type('john@test.com');
    cy.get('[data-testid="password-input"]').type('password123');
    
    // Submit form
    cy.get('[data-testid="login-button"]').click();
    
    // Wait for API call
    cy.wait('@loginRequest');
    
    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
    
    // Should store token
    cy.window().its('localStorage').invoke('getItem', 'token').should('eq', 'test-token');
  });

  it('should handle login error', () => {
    // Mock error API response
    cy.intercept('POST', '/api/v1/auth/login', {
      statusCode: 401,
      body: {
        status: 'error',
        error_code: 'E004',
        message: 'Invalid credentials'
      }
    }).as('loginRequest');
    
    // Fill form with invalid credentials
    cy.get('[data-testid="email-input"]').type('invalid@test.com');
    cy.get('[data-testid="password-input"]').type('wrongpassword');
    
    // Submit form
    cy.get('[data-testid="login-button"]').click();
    
    // Wait for API call
    cy.wait('@loginRequest');
    
    // Should show error message
    cy.contains('Invalid credentials').should('be.visible');
    
    // Should not redirect
    cy.url().should('include', '/login');
  });

  it('should disable button during submission', () => {
    // Mock slow API response
    cy.intercept('POST', '/api/v1/auth/login', {
      delay: 2000,
      statusCode: 200,
      body: { status: 'success' }
    }).as('loginRequest');
    
    // Fill form
    cy.get('[data-testid="email-input"]').type('john@test.com');
    cy.get('[data-testid="password-input"]').type('password123');
    
    // Submit form
    cy.get('[data-testid="login-button"]').click();
    
    // Button should be disabled
    cy.get('[data-testid="login-button"]').should('be.disabled');
    cy.get('[data-testid="login-button"]').should('contain', 'Logging in');
  });

  it('should navigate to registration page', () => {
    // Click register link
    cy.contains('Register here').click();
    
    // Should navigate to registration page
    cy.url().should('include', '/register');
  });

  it('should be responsive on mobile', () => {
    // Set mobile viewport
    cy.viewport('iphone-x');
    
    // Check form is still accessible
    cy.get('[data-testid="email-input"]').should('be.visible');
    cy.get('[data-testid="password-input"]').should('be.visible');
    cy.get('[data-testid="login-button"]').should('be.visible');
    
    // Check form fits on screen
    cy.get('[data-testid="login-form"]').should('be.visible');
  });
});
```

---

## UX Styling Guidelines

### 1. Color Palette
```css
:root {
  /* Primary Colors */
  --primary-blue: #2563eb;
  --primary-blue-hover: #1d4ed8;
  --primary-blue-light: #dbeafe;
  
  /* Secondary Colors */
  --secondary-gray: #64748b;
  --secondary-gray-light: #f1f5f9;
  
  /* Success/Error Colors */
  --success-green: #10b981;
  --error-red: #ef4444;
  --warning-orange: #f59e0b;
  
  /* Neutral Colors */
  --white: #ffffff;
  --black: #000000;
  --gray-50: #f8fafc;
  --gray-100: #f1f5f9;
  --gray-200: #e2e8f0;
  --gray-300: #cbd5e1;
  --gray-400: #94a3b8;
  --gray-500: #64748b;
  --gray-600: #475569;
  --gray-700: #334155;
  --gray-800: #1e293b;
  --gray-900: #0f172a;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}
```

### 2. Typography
```css
/* Font Family */
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Font Sizes */
.text-xs { font-size: 0.75rem; line-height: 1rem; }
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.text-base { font-size: 1rem; line-height: 1.5rem; }
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }
.text-xl { font-size: 1.25rem; line-height: 1.75rem; }
.text-2xl { font-size: 1.5rem; line-height: 2rem; }
.text-3xl { font-size: 1.875rem; line-height: 2.25rem; }

/* Font Weights */
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
```

### 3. Component Styling
```css
/* Login Container */
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, var(--gray-50) 0%, var(--gray-100) 100%);
  padding: 1rem;
}

/* Login Card */
.login-card {
  background: var(--white);
  border-radius: 1rem;
  box-shadow: var(--shadow-xl);
  padding: 2.5rem;
  width: 100%;
  max-width: 400px;
  border: 1px solid var(--gray-200);
}

/* Form Elements */
.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--gray-700);
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--gray-300);
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: all 0.2s ease;
  background: var(--white);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px var(--primary-blue-light);
}

.form-input.error {
  border-color: var(--error-red);
  box-shadow: 0 0 0 3px rgb(239 68 68 / 0.1);
}

/* Button Styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  min-height: 44px; /* Accessibility: minimum touch target */
}

.btn-primary {
  background: var(--primary-blue);
  color: var(--white);
  width: 100%;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-blue-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.btn-primary:disabled {
  background: var(--gray-400);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Password Toggle */
.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--gray-500);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: color 0.2s ease;
}

.password-toggle:hover {
  color: var(--gray-700);
}

/* Error Messages */
.error-message {
  color: var(--error-red);
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Success Messages */
.success-message {
  color: var(--success-green);
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Loading States */
.loading-spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .login-card {
    padding: 2rem 1.5rem;
    margin: 1rem;
  }
  
  .btn {
    min-height: 48px; /* Larger touch target on mobile */
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem 1rem;
  }
  
  .text-2xl {
    font-size: 1.25rem;
  }
}
```

### 4. Accessibility Guidelines
```css
/* Focus Indicators */
.form-input:focus,
.btn:focus {
  outline: 2px solid var(--primary-blue);
  outline-offset: 2px;
}

/* High Contrast Mode */
@media (prefers-contrast: high) {
  .form-input {
    border-width: 2px;
  }
  
  .btn {
    border: 2px solid currentColor;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .form-input,
  .btn {
    transition: none;
  }
  
  .loading-spinner {
    animation: none;
  }
}

/* Screen Reader Only */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

### 5. Animation and Transitions
```css
/* Smooth Transitions */
.login-card {
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Form Validation Animation */
.form-input.error {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* Button Loading State */
.btn-loading {
  position: relative;
  color: transparent;
}

.btn-loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
```

### 6. Best Practices Checklist
- ✅ **Color Contrast**: Ensure 4.5:1 ratio for normal text, 3:1 for large text
- ✅ **Touch Targets**: Minimum 44px for mobile, 48px for better accessibility
- ✅ **Keyboard Navigation**: All interactive elements accessible via keyboard
- ✅ **Screen Reader Support**: Proper ARIA labels and semantic HTML
- ✅ **Loading States**: Clear feedback during form submission
- ✅ **Error Handling**: Descriptive error messages with suggestions
- ✅ **Responsive Design**: Works on all screen sizes
- ✅ **Performance**: Optimized images and minimal bundle size
- ✅ **Security**: Input sanitization and CSRF protection
- ✅ **Progressive Enhancement**: Works without JavaScript
