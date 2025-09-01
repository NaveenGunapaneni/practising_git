import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore authentication state from localStorage on app start
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');

    if (savedToken && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setToken(savedToken);
        setUser(userData);
        axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
      } catch (error) {
        console.error('Error parsing saved user data:', error);
        // Clear invalid data
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        delete axios.defaults.headers.common['Authorization'];
      }
    }

    setLoading(false);
  }, []);

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  const login = async (email, password) => {
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post('/api/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      if (response.data.status === 'success') {
        const { access_token, user: userData } = response.data.data;
        setToken(access_token);
        setUser(userData);
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(userData));
        toast.success(`Welcome back, ${userData.user_name}! Login successful.`);
        return { success: true };
      }
    } catch (error) {
      console.error('Login error:', error);

      // Handle different error scenarios with professional messages
      if (error.code === 'ERR_NETWORK') {
        toast.error('Unable to connect to the server. Please check your internet connection and try again.');
        return { success: false, error: 'Network connection failed' };
      }

      // Handle API response errors
      if (error.response) {
        const status = error.response.status;
        const errorData = error.response.data;

        switch (status) {
          case 401:
            toast.error('Invalid email or password. Please check your credentials and try again.');
            return { success: false, error: 'Invalid credentials' };

          case 404:
            toast.error('Account not found. Please register first or check your email address.');
            return { success: false, error: 'Account not found' };

          case 422:
            // Validation errors
            if (errorData.details && Array.isArray(errorData.details)) {
              const validationMessages = errorData.details.map(detail => detail.message).join(', ');
              toast.error(`Please correct the following: ${validationMessages}`);
            } else {
              toast.error('Please check your input and try again.');
            }
            return { success: false, error: 'Validation failed' };

          case 429:
            toast.error('Too many login attempts. Please wait a few minutes before trying again.');
            return { success: false, error: 'Rate limit exceeded' };

          case 500:
            toast.error('Server error occurred. Please try again later or contact support.');
            return { success: false, error: 'Server error' };

          default:
            const message = errorData?.message || 'Login failed. Please try again.';
            toast.error(message);
            return { success: false, error: message };
        }
      }

      // Fallback for unexpected errors
      toast.error('An unexpected error occurred. Please try again.');
      return { success: false, error: 'Unexpected error' };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post('/api/v1/auth/register', userData);

      if (response.data.status === 'success') {
        toast.success(`Account created successfully for ${userData.user_name}! Please login with your credentials.`);
        return { success: true };
      }
    } catch (error) {
      console.error('Registration error:', error);

      // Handle different error scenarios with professional messages
      if (error.code === 'ERR_NETWORK') {
        toast.error('Unable to connect to the server. Please check your internet connection and try again.');
        return { success: false, error: 'Network connection failed' };
      }

      // Handle API response errors
      if (error.response) {
        const status = error.response.status;
        const errorData = error.response.data;

        switch (status) {
          case 400:
            if (errorData.message && errorData.message.includes('already exists')) {
              toast.error('An account with this email address already exists. Please login or use a different email.');
            } else {
              toast.error('Invalid registration data. Please check your information and try again.');
            }
            return { success: false, error: 'Registration data invalid' };

          case 409:
            toast.error('An account with this email address already exists. Please login or use a different email.');
            return { success: false, error: 'Account already exists' };

          case 422:
            // Validation errors
            if (errorData.details && Array.isArray(errorData.details)) {
              const validationMessages = errorData.details.map(detail => {
                // Make validation messages more user-friendly
                if (detail.field === 'email') {
                  return 'Please enter a valid email address';
                } else if (detail.field === 'password') {
                  return 'Password must be at least 6 characters long';
                } else if (detail.field === 'contact_phone') {
                  return 'Please enter a valid phone number';
                } else {
                  return detail.message;
                }
              }).join(', ');
              toast.error(`Please correct the following: ${validationMessages}`);
            } else {
              toast.error('Please check your input and try again.');
            }
            return { success: false, error: 'Validation failed' };

          case 429:
            toast.error('Too many registration attempts. Please wait a few minutes before trying again.');
            return { success: false, error: 'Rate limit exceeded' };

          case 500:
            toast.error('Server error occurred during registration. Please try again later or contact support.');
            return { success: false, error: 'Server error' };

          default:
            const message = errorData?.message || 'Registration failed. Please try again.';
            toast.error(message);
            return { success: false, error: message };
        }
      }

      // Fallback for unexpected errors
      toast.error('An unexpected error occurred during registration. Please try again.');
      return { success: false, error: 'Unexpected error' };
    }
  };

  const demoLogin = () => {
    const mockUser = {
      user_id: 'demo',
      user_name: 'Demo User',
      email: 'demo@geopulse.com'
    };

    const mockToken = 'demo-token-' + Date.now();

    setToken(mockToken);
    setUser(mockUser);
    localStorage.setItem('token', mockToken);
    localStorage.setItem('user', JSON.stringify(mockUser));
    toast.success('Demo login successful!');
    return { success: true };
  };

  const logout = () => {
    const userName = user?.user_name || 'User';
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    toast.success(`Goodbye, ${userName}! You have been logged out successfully.`);
  };

  const value = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    loading,
    login,
    register,
    logout,
    demoLogin,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
