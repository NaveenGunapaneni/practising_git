/**
 * Notification System Component
 * Displays toast notifications for user feedback
 */

import React, { createContext, useContext, useReducer } from 'react';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import './NotificationSystem.css';

// Notification types
const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

// Action types
const ACTIONS = {
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  CLEAR_ALL: 'CLEAR_ALL',
};

// Initial state
const initialState = {
  notifications: [],
};

// Reducer
function notificationReducer(state, action) {
  switch (action.type) {
    case ACTIONS.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [...state.notifications, action.payload],
      };

    case ACTIONS.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter(
          notification => notification.id !== action.payload
        ),
      };

    case ACTIONS.CLEAR_ALL:
      return {
        ...state,
        notifications: [],
      };

    default:
      return state;
  }
}

// Create context
const NotificationContext = createContext();

// Notification provider
export function NotificationProvider({ children }) {
  const [state, dispatch] = useReducer(notificationReducer, initialState);

  // Add notification
  const addNotification = (notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      type: NOTIFICATION_TYPES.INFO,
      duration: 5000,
      ...notification,
    };

    dispatch({
      type: ACTIONS.ADD_NOTIFICATION,
      payload: newNotification,
    });

    // Auto-remove notification after duration
    if (newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  };

  // Remove notification
  const removeNotification = (id) => {
    dispatch({
      type: ACTIONS.REMOVE_NOTIFICATION,
      payload: id,
    });
  };

  // Clear all notifications
  const clearAll = () => {
    dispatch({ type: ACTIONS.CLEAR_ALL });
  };

  // Convenience methods
  const success = (message, options = {}) => {
    return addNotification({
      type: NOTIFICATION_TYPES.SUCCESS,
      message,
      ...options,
    });
  };

  const error = (message, options = {}) => {
    return addNotification({
      type: NOTIFICATION_TYPES.ERROR,
      message,
      duration: 8000, // Longer duration for errors
      ...options,
    });
  };

  const warning = (message, options = {}) => {
    return addNotification({
      type: NOTIFICATION_TYPES.WARNING,
      message,
      duration: 6000,
      ...options,
    });
  };

  const info = (message, options = {}) => {
    return addNotification({
      type: NOTIFICATION_TYPES.INFO,
      message,
      ...options,
    });
  };

  const value = {
    notifications: state.notifications,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <NotificationContainer />
    </NotificationContext.Provider>
  );
}

// Notification container component
function NotificationContainer() {
  const { notifications, removeNotification } = useContext(NotificationContext);

  return (
    <div className="notification-container">
      {notifications.map((notification) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onRemove={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
}

// Individual notification item
function NotificationItem({ notification, onRemove }) {
  const { type, message, title, details, retryable, onRetry } = notification;

  // Get icon based on type
  const getIcon = () => {
    switch (type) {
      case NOTIFICATION_TYPES.SUCCESS:
        return <CheckCircle size={20} />;
      case NOTIFICATION_TYPES.ERROR:
        return <AlertCircle size={20} />;
      case NOTIFICATION_TYPES.WARNING:
        return <AlertTriangle size={20} />;
      case NOTIFICATION_TYPES.INFO:
      default:
        return <Info size={20} />;
    }
  };

  return (
    <div className={`notification notification--${type}`}>
      <div className="notification__icon">
        {getIcon()}
      </div>
      
      <div className="notification__content">
        {title && (
          <div className="notification__title">
            {title}
          </div>
        )}
        
        <div className="notification__message">
          {message}
        </div>
        
        {details && details.length > 0 && (
          <div className="notification__details">
            {details.map((detail, index) => (
              <div key={index} className="notification__detail">
                {typeof detail === 'string' ? detail : detail.message}
              </div>
            ))}
          </div>
        )}
        
        {retryable && onRetry && (
          <div className="notification__actions">
            <button
              className="notification__retry-btn"
              onClick={onRetry}
            >
              Retry
            </button>
          </div>
        )}
      </div>
      
      <button
        className="notification__close"
        onClick={onRemove}
        aria-label="Close notification"
      >
        <X size={16} />
      </button>
    </div>
  );
}

// Hook to use notifications
export function useNotifications() {
  const context = useContext(NotificationContext);
  
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  
  return context;
}

// Alias for convenience (used in components)
export function useNotification() {
  const context = useContext(NotificationContext);
  
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  
  return {
    showNotification: (message, type = 'info', options = {}) => {
      return context[type] ? context[type](message, options) : context.info(message, options);
    },
    success: context.success,
    error: context.error,
    warning: context.warning,
    info: context.info,
    clearAll: context.clearAll,
  };
}

// HOC to provide notification methods to components
export function withNotifications(Component) {
  return function NotificationComponent(props) {
    const notifications = useNotifications();
    return <Component {...props} notifications={notifications} />;
  };
}

export { NOTIFICATION_TYPES };
export default NotificationProvider;