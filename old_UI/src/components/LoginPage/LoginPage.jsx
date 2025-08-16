import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useNotification } from '../common/NotificationSystem';
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
    setErrors({});
    
    try {
      // Call the actual API using authService
      await login({
        username: formData.email,  // API expects 'username' field
        password: formData.password
      });
      
      showNotification('Login successful!', 'success');
      
      // Redirect to dashboard after successful login
      setTimeout(() => {
        window.location.replace('/dashboard');
      }, 1000); // Small delay to show success message
      
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = error.message || 'Login failed. Please check your credentials and try again.';
      setErrors({ general: errorMessage });
      showNotification(errorMessage, 'error');
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

          {/* General Error Message */}
          {errors.general && (
            <div className="error-message general-error" role="alert">
              {errors.general}
            </div>
          )}

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