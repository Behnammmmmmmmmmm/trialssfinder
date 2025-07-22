import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Trial } from '../types';
import { trialsAPI } from '../api/trials';
import { analyticsAPI } from '../api/analytics';
import { useAuth } from '../hooks/useStore';

export const TrialDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [trial, setTrial] = useState<Trial | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadTrial(parseInt(id));
    }
  }, [id]);

  const loadTrial = async (trialId: number) => {
    try {
      const response = await trialsAPI.get(trialId);
      setTrial(response.data);
    } catch (error) {
      console.error('Failed to load trial:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async () => {
    if (!user) {
      alert('Please log in to favorite this trial.');
      return;
    }
    if (!trial) {
      return;
    }

    try {
      await trialsAPI.toggleFavorite(trial.id);
      setTrial({ ...trial, is_favorited: !trial.is_favorited });
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const handleVisitTrial = async () => {
    if (!trial) {
      return;
    }
    await analyticsAPI.trackEvent({
      event_type: 'trial_start',
      trial: trial.id
    });
    alert('Redirecting to trial...');
  };

  if (loading) {
    return (
      <div className="container py-8 flex justify-center">
        <div className="spinner" data-size="lg"></div>
      </div>
    );
  }

  if (!trial) {
    return (
      <div className="container py-8 text-center">
        <h1 className="text-3xl font-bold mb-4">Trial Not Found</h1>
        <p className="text-muted mb-6">The trial you're looking for doesn't exist.</p>
        <Link to="/" className="btn" data-variant="primary">
          Back to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <div className="max-w-4xl mx-auto">
        <Link to="/" className="text-primary hover:underline mb-4 inline-block">
          ← Back to Trials
        </Link>
        
        <div className="card">
          <div className="card-body">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h1 className="text-3xl font-bold mb-2">{trial.title}</h1>
                <div className="flex items-center gap-4 text-muted">
                  <span>🏢 {trial.company_name}</span>
                  <span>🏭 {trial.industry_name}</span>
                  <span>📍 {trial.location}</span>
                </div>
              </div>
              <button
                onClick={handleToggleFavorite}
                className="btn"
                data-variant={trial.is_favorited ? "primary" : "outline"}
                title={trial.is_favorited ? "Remove from favorites" : "Add to favorites"}
              >
                {trial.is_favorited ? '★' : '☆'}
              </button>
            </div>
            
            <div className="prose max-w-none mb-8">
              <h2 className="text-xl font-semibold mb-3">Description</h2>
              <p className="text-muted whitespace-pre-wrap">{trial.description}</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold mb-2">Trial Period</h3>
                <p className="text-muted">
                  {new Date(trial.start_date).toLocaleDateString()} - {new Date(trial.end_date).toLocaleDateString()}
                </p>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold mb-2">Status</h3>
                <p className="text-muted">
                  {trial.is_featured && (
                    <span className="badge mr-2" data-variant="primary">Featured</span>
                  )}
                  <span className="badge" data-variant="success">Active</span>
                </p>
              </div>
            </div>
            
            <div className="text-center">
              <button 
                onClick={handleVisitTrial}
                className="btn"
                data-variant="primary"
                data-size="lg"
              >
                Start Free Trial →
              </button>
              <p className="text-sm text-muted mt-2">
                You'll be redirected to the company's trial signup page
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrialDetailsPage;