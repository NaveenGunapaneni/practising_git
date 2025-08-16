/**
 * Error Handler Utilities
 * Centralized error handling and user notification system
 */

// Error types
export const ERROR_TYPES = {
  VALIDATION: 'validation',
  AUTHENTICATION: 'authentication',
  AUTHORIZATION: 'authorization',
  NETWORK: 'network',
  SERVER: 'server',
  FILE_UPLOAD: 'file_upload',
  PROCESSING: 'processing',
  UNKNOWN: 'unknown',
};

// Error codes mapping
export const ERROR_CODES = {
  E001: { type: ERROR_TYPES.FILE_UPLOAD, message: 'Invalid file format or size' },
  E002: { type: ERROR_TYPES.FILE_UPLOAD, message: 'File size exceeds limit' },
  E003: { type: ERROR_TYPES.SERVER, message: 'Database or server error' },
  E004: { type: ERROR_TYPES.AUTHENTICATION, message: 'Authentication failed' },
  E005: { type: ERROR_TYPES.PROCESSING, message: 'File processing failed' },
  E006: { type: ERROR_TYPES.SERVER, message: 'Storage operation failed' },
  E007: { type: ERROR_TYPES.VALIDATION, message: 'Input validation failed' },
};

/**
 * Parse API error response and return structured error info
 */
export function parseApiError(error) {
  // Default error structure
  const errorInfo = {
    type: ERROR_TYPES.UNKNOWN,
    message: 'An unexpected error occurred',
    details: [],
    code: null,
    status: 0,
  };

  if (!error) {
    return errorInfo;
  }

  // Handle string errors
  if (typeof error === 'string') {
    errorInfo.message = error;
    return errorInfo;
  }

  // Handle API error objects
  if (error.status) {
    errorInfo.status = error.status;
  }

  if (error.data) {
    const { data } = error;
    
    // Extract error code
    if (data.error_code) {
      errorInfo.code = data.error_code;
      const codeInfo = ERROR_CODES[data.error_code];
      if (codeInfo) {
        errorInfo.type = codeInfo.type;
      }
    }

    // Extract message
    if (data.message) {
      errorInfo.message = data.message;
    } else if (data.detail?.message) {
      errorInfo.message = data.detail.message;
    }

    // Extract details
    if (data.details) {
      if (Array.isArray(data.details)) {
        errorInfo.details = data.details;
      } else if (typeof data.details === 'object') {
        errorInfo.details = [data.details];
      }
    } else if (data.detail?.details) {
      errorInfo.details = Array.isArray(data.detail.details) 
        ? data.detail.details 
        : [data.detail.details];
    }
  }

  // Handle network errors
  if (error.status === 0 || error.message?.includes('Network')) {
    errorInfo.type = ERROR_TYPES.NETWORK;
    errorInfo.message = 'Network connection failed. Please check your internet connection.';
  }

  // Handle authentication errors
  if (error.status === 401) {
    errorInfo.type = ERROR_TYPES.AUTHENTICATION;
    errorInfo.message = 'Authentication failed. Please log in again.';
  }

  // Handle authorization errors
  if (error.status === 403) {
    errorInfo.type = ERROR_TYPES.AUTHORIZATION;
    errorInfo.message = 'You do not have permission to perform this action.';
  }

  // Handle validation errors
  if (error.status === 422) {
    errorInfo.type = ERROR_TYPES.VALIDATION;
  }

  // Handle server errors
  if (error.status >= 500) {
    errorInfo.type = ERROR_TYPES.SERVER;
    errorInfo.message = 'Server error occurred. Please try again later.';
  }

  return errorInfo;
}

/**
 * Format error message for display to users
 */
export function formatErrorMessage(error) {
  const errorInfo = parseApiError(error);
  
  let message = errorInfo.message;

  // Add details if available
  if (errorInfo.details && errorInfo.details.length > 0) {
    const detailMessages = errorInfo.details
      .map(detail => {
        if (typeof detail === 'string') {
          return detail;
        }
        if (detail.field && detail.message) {
          return `${detail.field}: ${detail.message}`;
        }
        if (detail.message) {
          return detail.message;
        }
        return JSON.stringify(detail);
      })
      .filter(Boolean);

    if (detailMessages.length > 0) {
      message += '\n\nDetails:\n' + detailMessages.join('\n');
    }
  }

  return message;
}

/**
 * Get user-friendly error message based on error type
 */
export function getUserFriendlyMessage(error) {
  const errorInfo = parseApiError(error);

  switch (errorInfo.type) {
    case ERROR_TYPES.VALIDATION:
      return 'Please check your input and try again.';
    
    case ERROR_TYPES.AUTHENTICATION:
      return 'Please log in to continue.';
    
    case ERROR_TYPES.AUTHORIZATION:
      return 'You do not have permission to perform this action.';
    
    case ERROR_TYPES.NETWORK:
      return 'Please check your internet connection and try again.';
    
    case ERROR_TYPES.FILE_UPLOAD:
      return 'File upload failed. Please check the file format and size.';
    
    case ERROR_TYPES.PROCESSING:
      return 'File processing failed. Please try uploading again.';
    
    case ERROR_TYPES.SERVER:
      return 'Server error occurred. Please try again later.';
    
    default:
      return errorInfo.message || 'An unexpected error occurred.';
  }
}

/**
 * Check if error requires user re-authentication
 */
export function requiresReauth(error) {
  const errorInfo = parseApiError(error);
  return errorInfo.type === ERROR_TYPES.AUTHENTICATION || 
         errorInfo.status === 401 ||
         errorInfo.message?.toLowerCase().includes('token');
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error) {
  const errorInfo = parseApiError(error);
  return errorInfo.type === ERROR_TYPES.NETWORK || 
         errorInfo.status >= 500 ||
         errorInfo.status === 0;
}

/**
 * Get error severity level
 */
export function getErrorSeverity(error) {
  const errorInfo = parseApiError(error);

  switch (errorInfo.type) {
    case ERROR_TYPES.VALIDATION:
      return 'warning';
    
    case ERROR_TYPES.AUTHENTICATION:
    case ERROR_TYPES.AUTHORIZATION:
      return 'error';
    
    case ERROR_TYPES.NETWORK:
    case ERROR_TYPES.SERVER:
      return 'error';
    
    case ERROR_TYPES.FILE_UPLOAD:
    case ERROR_TYPES.PROCESSING:
      return 'error';
    
    default:
      return 'error';
  }
}

/**
 * Create notification object for toast/alert systems
 */
export function createErrorNotification(error, options = {}) {
  const errorInfo = parseApiError(error);
  
  return {
    type: 'error',
    severity: getErrorSeverity(error),
    title: options.title || 'Error',
    message: options.userFriendly 
      ? getUserFriendlyMessage(error)
      : formatErrorMessage(error),
    details: errorInfo.details,
    code: errorInfo.code,
    retryable: isRetryableError(error),
    requiresReauth: requiresReauth(error),
    timestamp: new Date().toISOString(),
    ...options,
  };
}

/**
 * Log error for debugging (in development)
 */
export function logError(error, context = '') {
  if (process.env.NODE_ENV === 'development') {
    console.group(`🚨 Error ${context ? `in ${context}` : ''}`);
    console.error('Original error:', error);
    console.error('Parsed error:', parseApiError(error));
    console.groupEnd();
  }
}

/**
 * Handle common error scenarios
 */
export const errorHandlers = {
  // Handle authentication errors
  handleAuthError: (error, authContext) => {
    if (requiresReauth(error)) {
      authContext?.logout();
      return {
        handled: true,
        action: 'redirect_to_login',
        message: 'Your session has expired. Please log in again.',
      };
    }
    return { handled: false };
  },

  // Handle file upload errors
  handleFileUploadError: (error) => {
    const errorInfo = parseApiError(error);
    
    if (errorInfo.code === 'E001') {
      return {
        handled: true,
        message: 'Please select a valid XLSX or CSV file.',
        suggestions: ['Check file format', 'Ensure file is not corrupted'],
      };
    }
    
    if (errorInfo.code === 'E002') {
      return {
        handled: true,
        message: 'File size is too large. Maximum size is 50MB.',
        suggestions: ['Reduce file size', 'Split large files'],
      };
    }

    return { handled: false };
  },

  // Handle validation errors
  handleValidationError: (error) => {
    const errorInfo = parseApiError(error);
    
    if (errorInfo.type === ERROR_TYPES.VALIDATION && errorInfo.details.length > 0) {
      const fieldErrors = {};
      errorInfo.details.forEach(detail => {
        if (detail.field) {
          fieldErrors[detail.field] = detail.message;
        }
      });

      return {
        handled: true,
        fieldErrors,
        message: 'Please correct the highlighted fields.',
      };
    }

    return { handled: false };
  },
};

const errorHandler = {
  parseApiError,
  formatErrorMessage,
  getUserFriendlyMessage,
  requiresReauth,
  isRetryableError,
  getErrorSeverity,
  createErrorNotification,
  logError,
  errorHandlers,
  ERROR_TYPES,
  ERROR_CODES,
};

export default errorHandler;