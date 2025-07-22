import api from '../utils/api';

export const subscriptionsAPI = {
  getPaymentMethods: () => api.get('/subscriptions/payment-methods/'),
  addPaymentMethod: (data: any) => api.post('/subscriptions/payment-methods/', data),
  deletePaymentMethod: (id: number) => api.delete(`/subscriptions/payment-methods/${id}/`),
  setDefaultPaymentMethod: (id: number) => api.post(`/subscriptions/payment-methods/${id}/set-default/`),
  getSubscriptions: () => api.get('/subscriptions/'),
  createSubscription: (data: any) => api.post('/subscriptions/create/', data),
  getInvoices: () => api.get('/subscriptions/invoices/'),
  updateAddress: (address: string) => api.post('/subscriptions/update-address/', { address }),
};