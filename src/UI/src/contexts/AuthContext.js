/**
 * Authentication Context
 * Manages user authentication state across the application
 */

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authService } from '../services/api';

// Initial state
const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  REGISTER_START: 'REGISTER_START',
  REGISTER_SUCCESS: 'REGISTER_SUCCESS',
  REGISTER_FAILURE: 'REGISTER_FAILURE',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_LOADING: 'SET_LOADING',
  RESTORE_SESSION: 'RESTORE_SESSION',
};

// Reducer function
function authReducer(state, action) {
  console.log("AuthContext - Reducer called with action:", action.type, action.payload);
  
  let newState;
  
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
    case AUTH_ACTIONS.REGISTER_START:
      newState = {
        ...state,
        isLoading: true,
        error: null,
      };
      break;

    case AUTH_ACTIONS.LOGIN_SUCCESS:
      newState = {
        ...state,
        user: action.payload.user,
        token: action.payload.access_token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
      console.log("AuthContext - LOGIN_SUCCESS new state:", newState);
      break;

    case AUTH_ACTIONS.REGISTER_SUCCESS:
      newState = {
        ...state,
        user: action.payload,
        isLoading: false,
        error: null,
      };
      break;

    case AUTH_ACTIONS.LOGIN_FAILURE:
    case AUTH_ACTIONS.REGISTER_FAILURE:
      newState = {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
      break;

    case AUTH_ACTIONS.LOGOUT:
      newState = {
        ...initialState,
        isLoading: false,
      };
      break;

    case AUTH_ACTIONS.CLEAR_ERROR:
      newState = {
        ...state,
        error: null,
      };
      break;

    case AUTH_ACTIONS.SET_LOADING:
      newState = {
        ...state,
        isLoading: action.payload,
      };
      break;

    case AUTH_ACTIONS.RESTORE_SESSION:
      newState = {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: !!action.payload.token,
        isLoading: false,
      };
      break;

    default:
      newState = state;
  }
  
  console.log("AuthContext - New state:", newState);
  return newState;
}

// Create context
const AuthContext = createContext();

// Auth provider component
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Restore session on app load
  useEffect(() => {
    const restoreSession = () => {
      console.log("AuthContext - Restoring session from localStorage");
      const token = localStorage.getItem('auth_token');
      const userData = localStorage.getItem('user_data');
      
      console.log("AuthContext - Found token:", token ? "Yes" : "No");
      console.log("AuthContext - Found userData:", userData ? "Yes" : "No");
      
      if (token && userData) {
        try {
          const user = JSON.parse(userData);
          console.log("AuthContext - Parsed user data:", user);
          dispatch({
            type: AUTH_ACTIONS.RESTORE_SESSION,
            payload: { user, token },
          });
          console.log("AuthContext - Session restored successfully");
        } catch (error) {
          console.error("AuthContext - Error parsing user data:", error);
          // Invalid stored data, clear it
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_data');
          dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
        }
      } else {
        console.log("AuthContext - No stored session found");
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
      }
    };

    restoreSession();
  }, []);

  // Login function
  const login = async (credentials) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });

    try {
      const response = await authService.login(credentials);
      
      console.log("AuthContext - Login response:", response);

      // Store user data in localStorage
      localStorage.setItem('user_data', JSON.stringify(response.user));
      
      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: response,
      });

      console.log("AuthContext - Login success dispatched");

      return response;
    } catch (error) {
      console.error("AuthContext - Login error:", error);
      const errorMessage = error.message || 'Login failed';
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: errorMessage,
      });

      throw error;
    }
  };

  // Register function
  const register = async (userData) => {
    dispatch({ type: AUTH_ACTIONS.REGISTER_START });

    try {
      const response = await authService.register(userData);

      dispatch({
        type: AUTH_ACTIONS.REGISTER_SUCCESS,
        payload: response.user || response,
      });

      return response;
    } catch (error) {
      const errorMessage = error.message || 'Registration failed';
      dispatch({
        type: AUTH_ACTIONS.REGISTER_FAILURE,
        payload: errorMessage,
      });

      throw error;
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.warn('Logout API call failed:', error);
    } finally {
      localStorage.removeItem('user_data');
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Context value
  const value = {
    // State
    user: state.user,
    token: state.token,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    error: state.error,

    // Actions
    login,
    register,
    logout,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

// HOC for protected routes
export function withAuth(Component) {
  return function AuthenticatedComponent(props) {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
      return (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      );
    }

    if (!isAuthenticated) {
      // Redirect to login or show login form
      return null;
    }

    return <Component {...props} />;
  };
}

export default AuthContext;