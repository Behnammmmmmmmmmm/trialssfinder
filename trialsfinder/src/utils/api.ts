import axios from 'axios';
import * as Sentry from '@sentry/react';
import { apiCache, setupCacheInterceptor } from './apiCache';
import { captureException } from './sentry';

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
  withCredentials: true, // Important for CSRF
  timeout: 30000, // 30 second timeout
});

// Get CSRF token from cookie
function getCookie(name: string) {
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

api.interceptors.request.use((config) => {
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
  
  // Add Sentry trace headers
  const transaction = Sentry.getCurrentHub().getScope()?.getTransaction();
  if (transaction) {
    const span = transaction.startChild({
      data: {
        type: 'fetch',
        url: config.url,
        method: config.method,
      },
      op: 'http',
      description: `${config.method?.toUpperCase()} ${config.url}`,
    });
    
    // Store span to finish it later
    (config as any).sentrySpan = span;
  }
  
  return config;
});

api.interceptors.response.use(
  (response) => {
    // Finish Sentry span
    const span = (response.config as any).sentrySpan;
    if (span) {
      span.setHttpStatus(response.status);
      span.finish();
    }
    
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Finish Sentry span with error
    const span = (originalRequest as any).sentrySpan;
    if (span) {
      span.setStatus('internal_error');
      span.finish();
    }
    
    // Capture network errors in Sentry
    if (!error.response && process.env.NODE_ENV === 'production') {
      captureException(error, {
        url: originalRequest?.url,
        method: originalRequest?.method,
        tags: {
          type: 'network_error',
        },
      });
    }
    
    // Handle network errors
    if (!error.response) {
      // Backend is not available
      if (process.env.NODE_ENV === 'development') {
        console.warn('Backend server is not running. Returning mock data.');
        
        // Return mock data based on the endpoint
        if (originalRequest.url.includes('/trials')) {
          return { 
            data: { 
              results: [], 
              count: 0, 
              next: null, 
              previous: null 
            } 
          };
        }
        
        if (originalRequest.url.includes('/auth/me')) {
          return Promise.reject(new Error('Not authenticated'));
        }
      }
      
      return Promise.reject(error);
    }
    
    // Capture 5xx errors in Sentry
    if (error.response?.status >= 500 && process.env.NODE_ENV === 'production') {
      captureException(error, {
        url: originalRequest?.url,
        method: originalRequest?.method,
        status: error.response.status,
        response: error.response.data,
        tags: {
          type: 'server_error',
        },
      });
    }
    
    // Handle 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token');
        }
        
        const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });
        
        localStorage.setItem('access_token', response.data.access);
        api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
        
        return api(originalRequest);
      } catch (refreshError) {
        // Clear cache on logout
        apiCache.invalidate();
        localStorage.clear();
        
        // Only redirect in production
        if (process.env.NODE_ENV === 'production') {
          window.location.href = '/login';
        }
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