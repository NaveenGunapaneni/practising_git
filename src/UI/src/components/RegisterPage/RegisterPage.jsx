import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Loader2, Check, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useNotification } from '../common/NotificationSystem';
import './RegisterPage.css';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const { showNotification } = useNotification();
  
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    organizationName: '',
    contactPhone: '',
    agreeToTerms: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [passwordValidation, setPasswordValidation] = useState({
    hasMinLength: false,
    hasUppercase: false,
    hasLowercase: false,
    hasNumber: false,
    passwordsMatch: false
  });
  const [showPasswordRequirements, setShowPasswordRequirements] = useState(false);

  // Real-time password validation
  useEffect(() => {
    const { password, confirmPassword } = formData;

    setPasswordValidation({
      hasMinLength: password.length >= 8,
      hasUppercase: /[A-Z]/.test(password),
      hasLowercase: /[a-z]/.test(password),
      hasNumber: /\d/.test(password),
      passwordsMatch: password === confirmPassword && password !== '' && confirmPassword !== ''
    });
  }, [formData]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handlePasswordFocus = () => {
    setShowPasswordRequirements(true);
  };

  const handlePasswordBlur = () => {
    // Keep requirements visible if password field has content or if there are validation errors
    if (!formData.password && !errors.password) {
      setShowPasswordRequirements(false);
    }
  };

  const isFormValid = () => {
    return (
      formData.fullName.trim() !== '' &&
      formData.email !== '' &&
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email) &&
      formData.organizationName.trim() !== '' &&
      formData.contactPhone.trim() !== '' &&
      passwordValidation.hasMinLength &&
      passwordValidation.hasUppercase &&
      passwordValidation.hasLowercase &&
      passwordValidation.hasNumber &&
      passwordValidation.passwordsMatch &&
      formData.agreeToTerms
    );
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!formData.organizationName.trim()) {
      newErrors.organizationName = 'Organization name is required';
    }

    if (!formData.contactPhone.trim()) {
      newErrors.contactPhone = 'Contact phone is required';
    } else if (!/^[\+]?[1-9][\d]{0,15}$/.test(formData.contactPhone.replace(/[\s\-\(\)]/g, ''))) {
      newErrors.contactPhone = 'Invalid phone number format';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (!passwordValidation.hasMinLength) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!passwordValidation.hasUppercase || !passwordValidation.hasLowercase || !passwordValidation.hasNumber) {
      newErrors.password = 'Must contain: uppercase, lowercase, number (min 8 chars)';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (!passwordValidation.passwordsMatch) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!formData.agreeToTerms) {
      newErrors.agreeToTerms = 'You must agree to the Terms of Service and Privacy Policy';
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
      await register({
        user_name: formData.fullName,
        email: formData.email,
        password: formData.password,
        organization_name: formData.organizationName,
        contact_phone: formData.contactPhone
      });
      
      showNotification('Registration successful! Please check your email to verify your account.', 'success');
      navigate('/login');
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({ general: error.message || 'Registration failed. Please try again.' });
      showNotification(error.message || 'Registration failed. Please try again.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        {/* Welcome Section */}
        <div className="welcome-section">
          <h1 className="welcome-title">Create Your Account</h1>
        </div>

        {/* Registration Form */}
        <form className="register-form" onSubmit={handleSubmit} data-testid="register-form">
          {/* Full Name Field */}
          <div className="form-group">
            <div className="input-wrapper">
              <input
                type="text"
                id="fullName"
                name="fullName"
                value={formData.fullName}
                onChange={handleInputChange}
                className={`form-input ${errors.fullName ? 'error' : ''}`}
                placeholder="FULL NAME"
                data-testid="fullname-input"
                autoComplete="name"
              />
            </div>
            {errors.fullName && (
              <div className="error-message" role="alert">
                {errors.fullName}
              </div>
            )}
          </div>

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

          {/* Organization Name Field */}
          <div className="form-group">
            <div className="input-wrapper">
              <input
                type="text"
                id="organizationName"
                name="organizationName"
                value={formData.organizationName}
                onChange={handleInputChange}
                className={`form-input ${errors.organizationName ? 'error' : ''}`}
                placeholder="ORGANIZATION NAME"
                data-testid="organization-input"
                autoComplete="organization"
              />
            </div>
            {errors.organizationName && (
              <div className="error-message" role="alert">
                {errors.organizationName}
              </div>
            )}
          </div>

          {/* Contact Phone Field */}
          <div className="form-group">
            <div className="input-wrapper">
              <input
                type="tel"
                id="contactPhone"
                name="contactPhone"
                value={formData.contactPhone}
                onChange={handleInputChange}
                className={`form-input ${errors.contactPhone ? 'error' : ''}`}
                placeholder="CONTACT PHONE"
                data-testid="phone-input"
                autoComplete="tel"
              />
            </div>
            {errors.contactPhone && (
              <div className="error-message" role="alert">
                {errors.contactPhone}
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
                onFocus={handlePasswordFocus}
                onBlur={handlePasswordBlur}
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder="CREATE PASSWORD"
                data-testid="password-input"
                autoComplete="new-password"
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
            {showPasswordRequirements && (
              <div className="password-requirements-list">
                <div className={`requirement ${passwordValidation.hasMinLength ? 'valid' : 'invalid'}`}>
                  {passwordValidation.hasMinLength ? <Check size={14} /> : <X size={14} />}
                  <span>At least 8 characters</span>
                </div>
                <div className={`requirement ${passwordValidation.hasUppercase ? 'valid' : 'invalid'}`}>
                  {passwordValidation.hasUppercase ? <Check size={14} /> : <X size={14} />}
                  <span>One uppercase letter</span>
                </div>
                <div className={`requirement ${passwordValidation.hasLowercase ? 'valid' : 'invalid'}`}>
                  {passwordValidation.hasLowercase ? <Check size={14} /> : <X size={14} />}
                  <span>One lowercase letter</span>
                </div>
                <div className={`requirement ${passwordValidation.hasNumber ? 'valid' : 'invalid'}`}>
                  {passwordValidation.hasNumber ? <Check size={14} /> : <X size={14} />}
                  <span>One number</span>
                </div>
              </div>
            )}
            {errors.password && (
              <div className="error-message" role="alert">
                {errors.password}
              </div>
            )}
          </div>

          {/* Confirm Password Field */}
          <div className="form-group">
            <div className="input-wrapper password-wrapper">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className={`form-input ${errors.confirmPassword ? 'error' : ''}`}
                placeholder="CONFIRM PASSWORD"
                data-testid="confirm-password-input"
                autoComplete="new-password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                data-testid="show-confirm-password-toggle"
                aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {formData.confirmPassword && (
              <div className={`password-match ${passwordValidation.passwordsMatch ? 'valid' : 'invalid'}`}>
                {passwordValidation.passwordsMatch ? <Check size={14} /> : <X size={14} />}
                <span>{passwordValidation.passwordsMatch ? 'Passwords match' : 'Passwords do not match'}</span>
              </div>
            )}
            {errors.confirmPassword && (
              <div className="error-message" role="alert">
                {errors.confirmPassword}
              </div>
            )}
          </div>

          {/* Terms Agreement */}
          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="agreeToTerms"
                checked={formData.agreeToTerms}
                onChange={handleInputChange}
                className="checkbox-input"
              />
              <span className="checkbox-custom"></span>
              <span className="checkbox-text">
                I agree to the{' '}
                <a href="/terms" className="terms-link">Terms of Service</a>
                {' '}and{' '}
                <a href="/privacy" className="terms-link">Privacy Policy</a>
              </span>
            </label>
            {errors.agreeToTerms && (
              <div className="error-message" role="alert">
                {errors.agreeToTerms}
              </div>
            )}
          </div>

          {/* Register Button */}
          <button
            type="submit"
            className={`btn btn-primary ${isLoading ? 'btn-loading' : ''}`}
            disabled={isLoading || !isFormValid()}
            data-testid="register-button"
          >
            {isLoading ? (
              <>
                <Loader2 className="loading-spinner" />
                Creating Account...
              </>
            ) : (
              'CREATE MY ACCOUNT'
            )}
          </button>

          {/* Login Link */}
          <div className="login-section">
            <span className="login-text">Already have an account? </span>
            <a href="/login" className="login-link">
              Sign in here
            </a>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterPage;