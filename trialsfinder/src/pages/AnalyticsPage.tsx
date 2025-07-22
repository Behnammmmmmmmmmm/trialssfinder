import React, { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { analyticsAPI } from '../api/analytics';
import { trialsAPI } from '../api/trials';
import { Trial } from '../types';

export const AnalyticsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [trials, setTrials] = useState<Trial[]>([]);
  const [selectedTrial, setSelectedTrial] = useState<number | null>(null);
  const [dateRange, setDateRange] = useState({
    start_date: '',
    end_date: ''
  });
  const [metrics, setMetrics] = useState<any>(null);

  const loadMetrics = useCallback(async () => {
    if (!selectedTrial) {
      return;
    }
    try {
      const response = await analyticsAPI.getTrialMetrics(selectedTrial, dateRange);
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  }, [selectedTrial, dateRange]);

  useEffect(() => {
    loadTrials();
    const trialId = searchParams.get('trial');
    if (trialId) {
      setSelectedTrial(parseInt(trialId));
    }
  }, [searchParams]);

  useEffect(() => {
    if (selectedTrial) {
      loadMetrics();
    }
  }, [selectedTrial, dateRange, loadMetrics]);

  const loadTrials = async () => {
    try {
      const response = await trialsAPI.companyTrials();
      // Handle both paginated and non-paginated responses
      const trialsData = response.data.results || response.data;
      setTrials(Array.isArray(trialsData) ? trialsData : []);
    } catch (error) {
      console.error('Failed to load trials:', error);
      setTrials([]);
    }
  };

  return (
    <div>
      <h1>Analytics Dashboard</h1>

      <div>
        <select 
          value={selectedTrial || ''} 
          onChange={(e) => setSelectedTrial(e.target.value ? parseInt(e.target.value) : null)}
        >
          <option value="">Select a trial</option>
          {trials.map(trial => (
            <option key={trial.id} value={trial.id}>{trial.title}</option>
          ))}
        </select>

        <input
          type="date"
          value={dateRange.start_date}
          onChange={(e) => setDateRange({...dateRange, start_date: e.target.value})}
        />
        <input
          type="date"
          value={dateRange.end_date}
          onChange={(e) => setDateRange({...dateRange, end_date: e.target.value})}
        />
      </div>

      {metrics && (
        <div>
          <h2>Summary Stats</h2>
          <p>Views: {metrics.views}</p>
          <p>Clicks: {metrics.clicks}</p>
          <p>Conversions: {metrics.conversions.toFixed(2)}%</p>

          <h2>Weekly Chart</h2>
          {metrics.weekly_data.map((day: any) => (
            <div key={day.date}>
              <span>{day.date}: Views: {day.views}, Clicks: {day.clicks}</span>
            </div>
          ))}

          <h2>Monthly Chart</h2>
          {metrics.monthly_data.map((day: any) => (
            <div key={day.date}>
              <span>{day.date}: Events: {day.events}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AnalyticsPage;