import axios from 'axios';

// Create Axios instance
const apiClient = axios.create({
  baseURL: `http://${window.location.hostname}:5000/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for API calls
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor for API calls
apiClient.interceptors.response.use(
  response => {
    return response.data; // Return data directly for convenience
  },
  error => {
    // Handle 401 Unauthorized globally
    if (error.response && error.response.status === 401) {
      // Clear local storage and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('name');
      
      // If we are not already on the login page, redirect
      if (window.location.hash !== '#/login' && window.location.pathname !== '/login') {
         window.location.href = '/#/login'; 
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
