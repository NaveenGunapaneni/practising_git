// Environment configuration
const config = {
  development: {
    API_BASE_URL: 'http://localhost:8000',
    API_TIMEOUT: 10000,
    DEBUG: true
  },
  production: {
    API_BASE_URL: process.env.REACT_APP_API_URL || 'https://api.geopulse.com',
    API_TIMEOUT: 15000,
    DEBUG: false
  }
};

const environment = process.env.NODE_ENV || 'development';

export default config[environment];