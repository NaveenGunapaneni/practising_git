import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { user, isAuthenticated, loading } = useAuth();

  console.log('ProtectedRoute - State:', { user, isAuthenticated, loading });

  if (loading) {
    console.log('ProtectedRoute - Loading state, showing spinner');
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <div style={{
          color: 'white',
          fontSize: '1.2rem',
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <div style={{
            width: '24px',
            height: '24px',
            border: '3px solid rgba(255, 255, 255, 0.3)',
            borderTop: '3px solid white',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }}></div>
          Loading...
        </div>
      </div>
    );
  }

  console.log('ProtectedRoute - Checking authentication:', { isAuthenticated, user });
  
  if (isAuthenticated && user) {
    console.log('ProtectedRoute - User authenticated, showing children');
    return children;
  } else {
    console.log('ProtectedRoute - User not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }
};

export default ProtectedRoute;