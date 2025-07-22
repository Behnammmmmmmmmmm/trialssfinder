import api from '../utils/api';

export const companiesAPI = {
  getProfile: () => api.get('/companies/profile/'),
  updateProfile: (data: any) => api.post('/companies/profile/', data),
};