// Email validation
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Password validation
export const validatePassword = (password) => {
  return password.length >= 6;
};

// Phone number validation
export const validatePhone = (phone) => {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
  return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
};

// File validation
export const validateFile = (file, maxSize = 50 * 1024 * 1024) => {
  const errors = [];

  // Check file type
  const allowedTypes = ['.xlsx', '.csv'];
  const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
  
  if (!allowedTypes.includes(fileExtension)) {
    errors.push('File must be XLSX or CSV format');
  }

  // Check file size
  if (file.size > maxSize) {
    errors.push(`File size must be less than ${maxSize / (1024 * 1024)}MB`);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

// Date validation
export const validateDate = (date) => {
  const dateObj = new Date(date);
  return dateObj instanceof Date && !isNaN(dateObj);
};

// Required field validation
export const validateRequired = (value) => {
  return value && value.trim().length > 0;
};

// Form validation helper
export const validateForm = (formData, rules) => {
  const errors = {};

  Object.keys(rules).forEach(field => {
    const value = formData[field];
    const fieldRules = rules[field];

    // Check required
    if (fieldRules.required && !validateRequired(value)) {
      errors[field] = `${field} is required`;
      return;
    }

    // Skip other validations if field is empty and not required
    if (!value && !fieldRules.required) {
      return;
    }

    // Email validation
    if (fieldRules.email && !validateEmail(value)) {
      errors[field] = 'Please enter a valid email address';
      return;
    }

    // Password validation
    if (fieldRules.password && !validatePassword(value)) {
      errors[field] = 'Password must be at least 6 characters long';
      return;
    }

    // Phone validation
    if (fieldRules.phone && !validatePhone(value)) {
      errors[field] = 'Please enter a valid phone number';
      return;
    }

    // Date validation
    if (fieldRules.date && !validateDate(value)) {
      errors[field] = 'Please enter a valid date';
      return;
    }

    // Min length validation
    if (fieldRules.minLength && value.length < fieldRules.minLength) {
      errors[field] = `${field} must be at least ${fieldRules.minLength} characters long`;
      return;
    }

    // Max length validation
    if (fieldRules.maxLength && value.length > fieldRules.maxLength) {
      errors[field] = `${field} must be no more than ${fieldRules.maxLength} characters long`;
      return;
    }

    // Custom validation
    if (fieldRules.custom) {
      const customError = fieldRules.custom(value, formData);
      if (customError) {
        errors[field] = customError;
        return;
      }
    }
  });

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Common validation rules
export const validationRules = {
  email: {
    required: true,
    email: true,
    maxLength: 255
  },
  password: {
    required: true,
    password: true,
    minLength: 6,
    maxLength: 255
  },
  organization_name: {
    required: true,
    maxLength: 255
  },
  user_name: {
    required: true,
    maxLength: 255
  },
  contact_phone: {
    required: true,
    phone: true,
    minLength: 10,
    maxLength: 20
  },
  engagement_name: {
    required: true,
    maxLength: 255
  },
  date1: {
    required: true,
    date: true
  },
  date2: {
    required: true,
    date: true
  },
  date3: {
    required: true,
    date: true
  },
  date4: {
    required: true,
    date: true
  }
};

// Format validation error messages
export const formatValidationErrors = (errors) => {
  return Object.values(errors).join(', ');
};
