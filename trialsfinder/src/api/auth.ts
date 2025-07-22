import api from '../utils/api';

interface RegisterData {
  username: string;
  email: string;
  password: string;
  user_type: 'user' | 'company';
  company_name?: string;
}

interface LoginData {
  username: string;
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