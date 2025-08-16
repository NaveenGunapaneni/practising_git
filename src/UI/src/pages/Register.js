import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Building2, Eye, EyeOff, Loader2 } from 'lucide-react';

// Logo component for login/register pages
const Logo = ({ className = "h-32 w-40" }) => {
  const [logoError, setLogoError] = useState(false);
  
  if (!logoError) {
    return (
      <img
        src="/images/AP_logo.png"
        alt="GeoPulse Logo"
        className={className}
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

    try {
      const result = await register(formData);
      if (result.success) {
        navigate('/login');
      }
    } catch (error) {
      console.error('Registration error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
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
                className="input-field mt-1"
                placeholder="Enter organization name"
                value={formData.organization_name}
                onChange={handleChange}
              />
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
                className="input-field mt-1"
                placeholder="Enter your full name"
                value={formData.user_name}
                onChange={handleChange}
              />
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
                className="input-field mt-1"
                placeholder="Enter phone number"
                value={formData.contact_phone}
                onChange={handleChange}
              />
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
                className="input-field mt-1"
                placeholder="Enter email address"
                value={formData.email}
                onChange={handleChange}
              />
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
                  className="input-field pr-10"
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
