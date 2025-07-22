import api from '../utils/api';

export const trialsAPI = {
  list: (params?: any) => api.get('/trials/', { params }),
  get: (id: number) => api.get(`/trials/${id}/`),
  create: (data: any) => api.post('/trials/create/', data),
  companyTrials: () => api.get('/trials/company/'),
  toggleFavorite: (id: number) => api.post(`/trials/${id}/favorite/`),
  getFavorites: () => api.get('/trials/favorites/'),
  getIndustries: () => api.get('/trials/industries/'),
  followIndustries: (industries: number[]) => api.post('/trials/industries/follow/', { industries }),
  getUserIndustries: () => api.get('/trials/industries/user/'),
  approveTrial: (id: number) => api.post(`/trials/${id}/approve/`),
  toggleFeatured: (id: number) => api.post(`/trials/${id}/toggle-featured/`),
  adminList: () => api.get('/trials/admin/'),
};