import { api } from '../utils/api';

interface RegisterData {
  email: string;
  password: string;
  confirm_password?: string;
  user_type: 'user' | 'company';
  company_name?: string;
}

interface LoginData {
  email: string;
  password: string;
}

interface ResetPasswordData {
  token: string;
  password: string;
}

export const authAPI = {
  register: (data: RegisterData) => api.post('/auth/register/', data),
  login: (data: LoginData) => api.post('/auth/login/', data),
  verifyEmail: (token: string) => api.post('/auth/verify-email/', { token }),
  forgotPassword: (email: string) => api.post('/auth/forgot-password/', { email }),
  resetPassword: (data: ResetPasswordData) => api.post('/auth/reset-password/', data),
  getMe: () => api.get('/auth/me/'),
};