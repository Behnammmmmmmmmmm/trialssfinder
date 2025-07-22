import api from '../utils/api';

export const analyticsAPI = {
  trackEvent: (data: any) => api.post('/analytics/events/', data),
  getTrialMetrics: (trialId: number, params?: any) => 
    api.get(`/analytics/trials/${trialId}/metrics/`, { params }),
};