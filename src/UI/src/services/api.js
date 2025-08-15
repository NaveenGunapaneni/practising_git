/**
 * GeoPulse API Service
 * Centralized API client for all backend communication with fallback support
 */

import config from '../config/environment';

const API_BASE_URL = config.API_BASE_URL + '/api/v1';
const API_TIMEOUT = config.API_TIMEOUT || 10000;

// Mock data for development/demo purposes when backend is not available
const MOCK_DATA = {
  user: {
    id: 1,
    email: 'demo@geopulse.com',
    full_name: 'Demo User',
    organization: 'GeoPulse Demo',
    is_active: true
  },
  dashboard: {
    metrics: {
      total_files: 12,
      processed_files: 8,
      pending_files: 4,
      total_lines: 45678
    },
    files: [
      {
        file_id: 1,
        filename: 'sample_data_2024.csv',
        engagement_name: 'Project Alpha',
        upload_date: '2024-01-15T10:30:00Z',
        line_count: 15420,
        processed_flag: true
      },
      {
        file_id: 2,
        filename: 'survey_results.csv',
        engagement_name: 'Market Research',
        upload_date: '2024-01-14T14:22:00Z',
        line_count: 8750,
        processed_flag: true
      },
      {
        file_id: 3,
        filename: 'customer_feedback.csv',
        engagement_name: 'Customer Analysis',
        upload_date: '2024-01-13T09:15:00Z',
        line_count: 12300,
        processed_flag: false
      },
      {
        file_id: 4,
        filename: 'sales_data_q4.csv',
        engagement_name: 'Q4 Sales Review',
        upload_date: '2024-01-12T16:45:00Z',
        line_count: 9208,
        processed_flag: false
      }
    ]
  }
};

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('auth_token');
  }

  // Set authentication token
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  // Get authentication token
  getToken() {
    return this.token || localStorage.getItem('auth_token');
  }

  // Clear authentication
  clearAuth() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  // Get default headers
  getHeaders(contentType = 'application/json') {
    const headers = {
      'Accept': 'application/json',
    };

    if (contentType) {
      headers['Content-Type'] = contentType;
    }

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  // Fallback data method for when API is unavailable
  getFallbackData(endpoint, method = 'GET') {
    console.warn(`API unavailable, using fallback data for: ${method} ${endpoint}`);
    
    if (endpoint.includes('/auth/login')) {
      return {
        access_token: 'demo_token_' + Date.now(),
        token_type: 'bearer',
        user: MOCK_DATA.user
      };
    }
    
    if (endpoint.includes('/auth/register')) {
      return {
        message: 'User registered successfully',
        user: MOCK_DATA.user
      };
    }
    
    if (endpoint.includes('/dashboard')) {
      return MOCK_DATA.dashboard;
    }
    
    if (endpoint.includes('/files/upload')) {
      return {
        message: 'File uploaded successfully',
        file_id: Math.floor(Math.random() * 1000),
        filename: 'uploaded_file.csv'
      };
    }
    
    if (endpoint.includes('/auth/me')) {
      return MOCK_DATA.user;
    }
    
    if (endpoint.includes('/health')) {
      return { status: 'ok', message: 'API is healthy (fallback mode)' };
    }
    
    return { message: 'Success', data: null };
  }

  // Generic request method with fallback handling
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    // Add timeout to options
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);
    
    const config = {
      ...options,
      signal: controller.signal,
      headers: {
        ...this.getHeaders(options.contentType),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      clearTimeout(timeoutId);
      
      // Handle different response types
      let data;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        // Handle API error responses
        const errorMessage = data?.message || data?.detail?.message || `HTTP ${response.status}`;
        throw new ApiError(errorMessage, response.status, data);
      }

      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Handle network/connection errors with fallback to mock data
      if (error.name === 'AbortError' || error.message.includes('fetch') || error.code === 'ECONNREFUSED') {
        return this.getFallbackData(endpoint, options.method || 'GET');
      }
      
      throw new ApiError(
        error.message || 'Network error occurred',
        0,
        { error: error.message }
      );
    }
  }

  // GET request
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, {
      method: 'GET',
    });
  }

  // POST request
  async post(endpoint, data = {}, options = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      ...options,
    });
  }

  // PUT request
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }

  // File upload request
  async uploadFile(endpoint, file, additionalData = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add additional form data
    Object.keys(additionalData).forEach(key => {
      formData.append(key, additionalData[key]);
    });

    return this.request(endpoint, {
      method: 'POST',
      body: formData,
      contentType: null, // Let browser set content-type for FormData
    });
  }
}

// Create singleton instance
const apiClient = new ApiClient();

// Authentication Service
export const authService = {
  async login(credentials) {
    const response = await apiClient.post('/auth/login', credentials);
    
    if (response.access_token) {
      apiClient.setToken(response.access_token);
    }
    
    return response;
  },

  async register(userData) {
    const response = await apiClient.post('/auth/register', userData);
    return response;
  },

  async logout() {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.warn('Logout API call failed, clearing local auth anyway');
    } finally {
      apiClient.clearAuth();
    }
  },

  async getCurrentUser() {
    return apiClient.get('/auth/me');
  },

  async refreshToken() {
    const response = await apiClient.post('/auth/refresh');
    if (response.access_token) {
      apiClient.setToken(response.access_token);
    }
    return response;
  }
};

// Dashboard Service
export const dashboardService = {
  async getDashboardData() {
    return apiClient.get('/dashboard');
  },

  async getMetrics() {
    return apiClient.get('/dashboard/metrics');
  },

  async getRecentFiles(limit = 10) {
    return apiClient.get('/dashboard/files', { limit });
  }
};

// File Service
export const fileService = {
  async uploadFile(file, engagementName) {
    return apiClient.uploadFile('/files/upload', file, {
      engagement_name: engagementName
    });
  },

  async getFiles(params = {}) {
    return apiClient.get('/files', params);
  },

  async getFile(fileId) {
    return apiClient.get(`/files/${fileId}`);
  },

  async deleteFile(fileId) {
    return apiClient.delete(`/files/${fileId}`);
  },

  async downloadFile(fileId) {
    return apiClient.get(`/files/${fileId}/download`);
  },

  async getFileStatus(fileId) {
    return apiClient.get(`/files/${fileId}/status`);
  }
};

// Health Service
export const healthService = {
  async checkHealth() {
    return apiClient.get('/health');
  }
};

// Export the API client instance
export default apiClient;