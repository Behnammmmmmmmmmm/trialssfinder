import { StateCreator } from 'zustand';
import * as Sentry from '@sentry/react';
import { User } from '../../types';
import { authAPI } from '../../api/auth';
import { AppState } from '../index';
import { setUser as setSentryUser, captureException } from '../../utils/sentry';

export interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
  mockMode: boolean;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setMockMode: (mockMode: boolean) => void;
  login: (username: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const createAuthSlice: StateCreator<AppState, [], [], AuthState> = (set) => ({
  user: null,
  loading: true,
  error: null,
  mockMode: false,

  setUser: (user) => {
    set({ user });
    // Update Sentry user context
    if (user) {
      setSentryUser({
        id: user.id,
        username: user.username,
        email: user.email,
      });
    } else {
      setSentryUser(null);
    }
  },
  
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setMockMode: (mockMode) => set({ mockMode }),

  login: async (username, password) => {
    set({ loading: true, error: null });
    
    const transaction = Sentry.startTransaction({
      name: 'auth.login',
      op: 'auth',
    });
    
    Sentry.getCurrentHub().configureScope(scope => scope.setSpan(transaction));
    
    try {
      const response = await authAPI.login({ username, password });
      const { tokens, user } = response.data;
      
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      
      set({ user, loading: false, mockMode: false });
      
      // Set Sentry user context
      setSentryUser({
        id: user.id,
        username: user.username,
        email: user.email,
      });
      
      transaction.setStatus('ok');
    } catch (error: any) {
      transaction.setStatus('internal_error');
      
      // In development, allow mock login
      if (process.env.NODE_ENV === 'development' && error.code === 'ERR_NETWORK') {
        console.warn('Backend not available, using mock login');
        const mockUser: User = {
          id: 1,
          username: username,
          email: `${username}@example.com`,
          user_type: 'user',
          email_verified: true
        };
        set({ user: mockUser, loading: false, mockMode: true });
        localStorage.setItem('mock_user', JSON.stringify(mockUser));
      } else {
        captureException(error, {
          username,
          tags: { feature: 'auth', action: 'login' },
        });
        set({ error: error.message || 'Login failed', loading: false });
        throw error;
      }
    } finally {
      transaction.finish();
    }
  },

  register: async (data) => {
    set({ loading: true, error: null });
    
    const transaction = Sentry.startTransaction({
      name: 'auth.register',
      op: 'auth',
    });
    
    Sentry.getCurrentHub().configureScope(scope => scope.setSpan(transaction));
    
    try {
      const response = await authAPI.register(data);
      const { tokens, user } = response.data;
      
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      
      if (response.data.verification_token) {
        localStorage.setItem('verification_token', response.data.verification_token);
      }
      
      set({ user, loading: false, mockMode: false });
      
      // Set Sentry user context
      setSentryUser({
        id: user.id,
        username: user.username,
        email: user.email,
      });
      
      transaction.setStatus('ok');
    } catch (error: any) {
      transaction.setStatus('internal_error');
      
      // In development, allow mock registration
      if (process.env.NODE_ENV === 'development' && error.code === 'ERR_NETWORK') {
        console.warn('Backend not available, using mock registration');
        const mockUser: User = {
          id: Date.now(),
          username: data.username,
          email: data.email,
          user_type: data.user_type || 'user',
          email_verified: false
        };
        set({ user: mockUser, loading: false, mockMode: true });
        localStorage.setItem('mock_user', JSON.stringify(mockUser));
      } else {
        captureException(error, {
          username: data.username,
          user_type: data.user_type,
          tags: { feature: 'auth', action: 'register' },
        });
        set({ error: error.message || 'Registration failed', loading: false });
        throw error;
      }
    } finally {
      transaction.finish();
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('verification_token');
    localStorage.removeItem('mock_user');
    set({ user: null, loading: false, error: null, mockMode: false });
    setSentryUser(null);
  },

  loadUser: async () => {
    const token = localStorage.getItem('access_token');
    const mockUser = localStorage.getItem('mock_user');
    
    // Check for mock user first (development only)
    if (process.env.NODE_ENV === 'development' && mockUser && !token) {
      try {
        const user = JSON.parse(mockUser);
        set({ user, loading: false, mockMode: true });
        setSentryUser({
          id: user.id,
          username: user.username,
          email: user.email,
        });
        return;
      } catch (e) {
        localStorage.removeItem('mock_user');
      }
    }
    
    if (!token) {
      set({ user: null, loading: false });
      return;
    }

    set({ loading: true });
    try {
      const response = await authAPI.getMe();
      const user = response.data;
      set({ user, loading: false, mockMode: false });
      setSentryUser({
        id: user.id,
        username: user.username,
        email: user.email,
      });
    } catch (error: any) {
      // In development, check if we have a mock user
      if (process.env.NODE_ENV === 'development' && error.code === 'ERR_NETWORK' && mockUser) {
        try {
          const user = JSON.parse(mockUser);
          set({ user, loading: false, mockMode: true });
          setSentryUser({
            id: user.id,
            username: user.username,
            email: user.email,
          });
          return;
        } catch (e) {
          // Invalid mock user
        }
      }
      
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('mock_user');
      set({ user: null, loading: false });
      setSentryUser(null);
    }
  },
});