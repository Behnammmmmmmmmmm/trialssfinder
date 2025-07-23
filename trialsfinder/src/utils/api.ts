import axios from 'axios';
import { apiCache, setupCacheInterceptor } from './apiCache';

// Use proxy for development, direct path for production
const API_BASE_URL = process.env.NODE_ENV === 'development'
  ? '/api'  // This will use the proxy defined in webpack.config.js
  : '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    common: {
      'Content-Type': 'application/json',
    },
  },
  withCredentials: true,  // Important for CSRF
  timeout: 30000,  // 30 second timeout
});

// Get CSRF token from cookie
function getCookie(name: string): string | null {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Setup cache interceptor
setupCacheInterceptor(api);

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add CSRF token for non-GET requests
    if (config.method !== 'get') {
      const csrfToken = getCookie('csrftoken');
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }

    // Add security headers
    config.headers['X-Requested-With'] = 'XMLHttpRequest';

    // Ensure URLs have trailing slashes for Django
    if (config.url && !config.url.endsWith('/') && !config.url.includes('?')) {
      config.url += '/';
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle network errors
    if (!error.response) {
      // Backend is not available
      if (process.env.NODE_ENV === 'development') {
        console.warn('Backend server is not running. Returning mock data.');
        
        // Return mock data based on the endpoint
        if (originalRequest.url?.includes('trials')) {
          return {
            data: {
              results: [],
              count: 0,
              next: null,
              previous: null,
            },
          };
        }
        
        if (originalRequest.url?.includes('auth/me')) {
          return Promise.reject(new Error('Not authenticated'));
        }
        
        return Promise.reject(error);
      }
      
      return Promise.reject(error);
    }

    // Handle 401 errors
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');

        const response = await axios.post(
          `${API_BASE_URL}/auth/refresh/`,
          { refresh: refreshToken }
        );

        localStorage.setItem('access_token', response.data.access);
        api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;

        return api(originalRequest);
      } catch (refreshError) {
        // Clear cache on logout
        apiCache.invalidate('');
        localStorage.clear();
        
        // Only redirect in production
        if (process.env.NODE_ENV === 'production') {
          window.location.href = '/login';
        }
        
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

// Cache invalidation helpers
export const invalidateUserCache = (userId: number) => {
  apiCache.invalidateUser(userId);
};

export const invalidateTrialCache = (trialId: number) => {
  apiCache.invalidateTrial(trialId);
};

export default api;