import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Building2, Eye, EyeOff, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

// Logo component for login/register pages
const Logo = ({ className = "h-32 w-40" }) => {
  const [logoError, setLogoError] = useState(false);
  
  if (!logoError) {
    return (
      <img
        src="/images/AP_logo2.avif"
        alt="GeoPulse Logo"
        className={`${className} border-0 outline-none`}
        style={{ border: 'none', outline: 'none' }}
        onError={() => setLogoError(true)}
      />
    );
  }

  return <Building2 className={`${className} text-primary-600`} />;
};

const Register = () => {
  const [formData, setFormData] = useState({
    organization_name: '',
    user_name: '',
    contact_phone: '',
    email: '',
    password: '',
    logo_path: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({}); // Clear previous errors

    try {
      const result = await register(formData);
      if (result.success) {
        navigate('/login');
      }
    } catch (error) {
      console.error('Registration error:', error);
      
      // Handle validation errors from API
      if (error.response?.data?.details) {
        const validationErrors = {};
        error.response.data.details.forEach(detail => {
          validationErrors[detail.field] = detail.message;
        });
        setErrors(validationErrors);
      } else {
        // Handle generic errors
        const message = error.response?.data?.message || 'Registration failed. Please try again.';
        toast.error(message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Watermark Background */}
      <div 
        className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none"
        style={{
          backgroundImage: 'url(/images/AP_logo2.avif)',
          backgroundSize: 'contain',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          transform: 'scale(1.25)',
          zIndex: 0
        }}
      />
      
      <div className="max-w-md w-full space-y-8 relative z-10">
                 <div>
           <div className="mx-auto flex items-center justify-center">
             <Logo className="h-32 w-40" />
           </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link
              to="/login"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              sign in to your existing account
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="organization_name" className="block text-sm font-medium text-gray-700">
                Organization Name
              </label>
              <input
                id="organization_name"
                name="organization_name"
                type="text"
                required
                className={`input-field mt-1 ${errors.organization_name ? 'border-red-500' : ''}`}
                placeholder="Enter organization name"
                value={formData.organization_name}
                onChange={handleChange}
              />
              {errors.organization_name && (
                <p className="mt-1 text-sm text-red-600">{errors.organization_name}</p>
              )}
            </div>

            <div>
              <label htmlFor="user_name" className="block text-sm font-medium text-gray-700">
                Full Name
              </label>
              <input
                id="user_name"
                name="user_name"
                type="text"
                required
                className={`input-field mt-1 ${errors.user_name ? 'border-red-500' : ''}`}
                placeholder="Enter your full name"
                value={formData.user_name}
                onChange={handleChange}
              />
              {errors.user_name && (
                <p className="mt-1 text-sm text-red-600">{errors.user_name}</p>
              )}
            </div>

            <div>
              <label htmlFor="contact_phone" className="block text-sm font-medium text-gray-700">
                Contact Phone
              </label>
              <input
                id="contact_phone"
                name="contact_phone"
                type="tel"
                required
                className={`input-field mt-1 ${errors.contact_phone ? 'border-red-500' : ''}`}
                placeholder="Enter phone number (e.g., +91-98765-43210 or 9876543210)"
                value={formData.contact_phone}
                onChange={handleChange}
              />
              {errors.contact_phone && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.contact_phone === 'Invalid phone number format' 
                    ? 'Please enter a valid phone number with at least 10 digits. Examples: +91-98765-43210, 9876543210, or 98765 43210'
                    : errors.contact_phone}
                </p>
              )}
              <p className="mt-1 text-xs text-gray-500">
                Enter your phone number with country code (e.g., +91 for India) or without. Minimum 10 digits required.
              </p>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className={`input-field mt-1 ${errors.email ? 'border-red-500' : ''}`}
                placeholder="Enter email address"
                value={formData.email}
                onChange={handleChange}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.email === 'Invalid email format' 
                    ? 'Please enter a valid email address (e.g., user@example.com)'
                    : errors.email}
                </p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="relative mt-1">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  required
                  className={`input-field pr-10 ${errors.password ? 'border-red-500' : ''}`}
                  placeholder="Enter password (min 6 characters)"
                  value={formData.password}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.password === 'Password must be at least 6 characters long' 
                    ? 'Password must be at least 6 characters long'
                    : errors.password}
                </p>
              )}
            </div>

            <div>
              <label htmlFor="logo_path" className="block text-sm font-medium text-gray-700">
                Logo Path (Optional)
              </label>
              <input
                id="logo_path"
                name="logo_path"
                type="text"
                className="input-field mt-1"
                placeholder="Enter logo file path"
                value={formData.logo_path}
                onChange={handleChange}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                'Create Account'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
