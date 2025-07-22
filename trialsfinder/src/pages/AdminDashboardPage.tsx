import React, { useEffect, useState } from 'react';
import { trialsAPI } from '../api/trials';
import { Trial } from '../types';

export const AdminDashboardPage: React.FC = () => {
  const [trials, setTrials] = useState<Trial[]>([]);

  useEffect(() => {
    loadTrials();
  }, []);

  const loadTrials = async () => {
    try {
      const response = await trialsAPI.adminList();
      // Handle both paginated and non-paginated responses
      const trialsData = response.data.results || response.data;
      setTrials(Array.isArray(trialsData) ? trialsData : []);
    } catch (error) {
      console.error('Failed to load trials:', error);
      setTrials([]);
    }
  };

  const handleApprove = async (trialId: number) => {
    try {
      await trialsAPI.approveTrial(trialId);
      loadTrials();
    } catch (error) {
      console.error('Failed to approve trial:', error);
    }
  };

  const handleToggleFeatured = async (trialId: number) => {
    try {
      await trialsAPI.toggleFeatured(trialId);
      loadTrials();
    } catch (error) {
      console.error('Failed to toggle featured:', error);
    }
  };

  return (
    <div>
      <h1>Admin Dashboard</h1>
      <h2>All Trials</h2>
      {trials.map(trial => (
        <div key={trial.id}>
          <h3>{trial.title}</h3>
          <p>Status: {trial.status}</p>
          <p>Featured: {trial.is_featured ? 'Yes' : 'No'}</p>
          {trial.status === 'under_review' && (
            <button onClick={() => handleApprove(trial.id)}>Approve</button>
          )}
          <button onClick={() => handleToggleFeatured(trial.id)}>
            {trial.is_featured ? 'Unfeature' : 'Feature'}
          </button>
        </div>
      ))}
    </div>
  );
};

export default AdminDashboardPage;