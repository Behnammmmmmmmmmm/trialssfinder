import api from '../utils/api';

export const notificationsAPI = {
  list: () => api.get('/notifications/'),
  markRead: (id: number) => api.post(`/notifications/${id}/read/`),
  contact: (data: any) => api.post('/notifications/contact/', data),
};