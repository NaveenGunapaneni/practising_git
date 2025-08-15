import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useNotification } from '../common/NotificationSystem';
// Error handling utilities available if needed
// import { errorHandlers, logError } from '../../utils/errorHandler';
import './LoginPage.css';

const LoginPage = () => {
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const { showNotification } = useNotification();
  
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      window.location.replace('/dashboard');
    }
  }, [isAuthenticated, authLoading]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log('Login attempt:', formData);
      
      // Check if user is registered
      const registeredUser = localStorage.getItem('registeredUser');
      if (registeredUser) {
        const userData = JSON.parse(registeredUser);
        
        // Validate credentials
        if (userData.email === formData.email && userData.password === formData.password) {
          // Create user info from registered data
          const emailDomain = formData.email.split('@')[1];
          const orgName = emailDomain.includes('gmail') || emailDomain.includes('yahoo') || emailDomain.includes('hotmail') || emailDomain.includes('outlook') 
            ? 'Geo Pulse' 
            : emailDomain.split('.')[0].replace(/\b\w/g, l => l.toUpperCase()) + ' Corp';
          
          const userInfo = {
            user_name: userData.fullName || formData.email.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            email: formData.email,
            organization_name: orgName
          };
          
          // Store token and user info
          localStorage.setItem('token', 'mock-jwt-token');
          localStorage.setItem('userInfo', JSON.stringify(userInfo));
          
          // Use replace to prevent back button issues
          window.location.replace('/dashboard');
        } else {
          setErrors({ general: 'Invalid email or password. Please try again.' });
        }
      } else {
        // For demo purposes, allow any login if no registered user
        const emailDomain = formData.email.split('@')[1];
        const orgName = emailDomain.includes('gmail') || emailDomain.includes('yahoo') || emailDomain.includes('hotmail') || emailDomain.includes('outlook') 
          ? 'Geo Pulse' 
          : emailDomain.split('.')[0].replace(/\b\w/g, l => l.toUpperCase()) + ' Corp';
        
        const userInfo = {
          user_name: formData.email.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          email: formData.email,
          organization_name: orgName
        };
        
        localStorage.setItem('token', 'mock-jwt-token');
        localStorage.setItem('userInfo', JSON.stringify(userInfo));
        window.location.replace('/dashboard');
      }
    } catch (error) {
      console.error('Login error:', error);
      setErrors({ general: 'Login failed. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        {/* Welcome Section */}
        <div className="welcome-section">
          <h1 className="welcome-title">Welcome to Geo Pulse</h1>
        </div>

        {/* Login Form */}
        <form className="login-form" onSubmit={handleSubmit} data-testid="login-form">
          {/* Email Field */}
          <div className="form-group">
            <div className="input-wrapper">
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={`form-input ${errors.email ? 'error' : ''}`}
                placeholder="EMAIL ADDRESS"
                data-testid="email-input"
                autoComplete="email"
              />
            </div>
            {errors.email && (
              <div className="error-message" role="alert">
                {errors.email}
              </div>
            )}
          </div>

          {/* Password Field */}
          <div className="form-group">
            <div className="input-wrapper password-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder="PASSWORD"
                data-testid="password-input"
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                data-testid="show-password-toggle"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {errors.password && (
              <div className="error-message" role="alert">
                {errors.password}
              </div>
            )}
          </div>

          {/* Forgot Password Link */}
          <div className="forgot-password-section">
            <a href="/forgot-password" className="forgot-link">
              Forgot your password?
            </a>
          </div>

          {/* Login Button */}
          <button
            type="submit"
            className={`btn btn-primary ${isLoading ? 'btn-loading' : ''}`}
            disabled={isLoading}
            data-testid="login-button"
          >
            {isLoading ? (
              <>
                <Loader2 className="loading-spinner" size={20} />
                Logging in...
              </>
            ) : (
              'LOGIN'
            )}
          </button>

          {/* Register Link */}
          <div className="register-section">
            <span className="register-text">Don't have an account? </span>
            <a href="/register" className="register-link">
              Create New Account
            </a>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;