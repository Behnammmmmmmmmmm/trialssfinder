import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useStore';
import { trialsAPI } from '../api/trials';
import { Trial } from '../types';

export const CompanyDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [trials, setTrials] = useState<Trial[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrials();
  }, []);

  const loadTrials = async () => {
    try {
      const response = await trialsAPI.companyTrials();
      const trialsData = response.data.results || response.data;
      setTrials(Array.isArray(trialsData) ? trialsData : []);
    } catch (error) {
      console.error('Failed to load trials:', error);
      setTrials([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      'draft': 'secondary',
      'under_review': 'warning',
      'approved': 'success',
      'rejected': 'danger'
    };
    return variants[status] || 'secondary';
  };

  if (loading) {
    return (
      <div className="container py-8 flex justify-center">
        <div className="spinner" data-size="lg"></div>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Company Dashboard</h1>
          <p className="text-muted mt-2">Welcome back, {user?.username}!</p>
        </div>
        <Link to="/create-trial" className="btn" data-variant="primary">
          <span className="mr-2">+</span> Create New Trial
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Link to="/company-profile" className="card hover:shadow-lg transition-shadow">
          <div className="card-body text-center">
            <div className="text-4xl mb-3">🏢</div>
            <h3 className="text-lg font-semibold">Company Profile</h3>
            <p className="text-sm text-muted">Manage your company info</p>
          </div>
        </Link>
        
        <Link to="/create-trial" className="card hover:shadow-lg transition-shadow">
          <div className="card-body text-center">
            <div className="text-4xl mb-3">➕</div>
            <h3 className="text-lg font-semibold">Create Trial</h3>
            <p className="text-sm text-muted">List a new free trial</p>
          </div>
        </Link>
        
        <Link to="/subscription" className="card hover:shadow-lg transition-shadow">
          <div className="card-body text-center">
            <div className="text-4xl mb-3">💳</div>
            <h3 className="text-lg font-semibold">Subscription</h3>
            <p className="text-sm text-muted">Manage billing & plans</p>
          </div>
        </Link>
        
        <Link to="/analytics" className="card hover:shadow-lg transition-shadow">
          <div className="card-body text-center">
            <div className="text-4xl mb-3">📊</div>
            <h3 className="text-lg font-semibold">Analytics</h3>
            <p className="text-sm text-muted">View performance data</p>
          </div>
        </Link>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold">Your Trials</h2>
        </div>
        <div className="card-body">
          {trials.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📋</div>
              <p className="text-xl text-muted mb-4">No trials created yet</p>
              <Link to="/create-trial" className="btn" data-variant="primary">
                Create Your First Trial
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3">Title</th>
                    <th className="text-left p-3">Status</th>
                    <th className="text-left p-3">Created</th>
                    <th className="text-left p-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {trials.map(trial => (
                    <tr key={trial.id} className="border-b hover:bg-gray-50">
                      <td className="p-3">
                        <div>
                          <p className="font-medium">{trial.title}</p>
                          <p className="text-sm text-muted">{trial.industry_name}</p>
                        </div>
                      </td>
                      <td className="p-3">
                        <span 
                          className="badge" 
                          data-variant={getStatusBadge(trial.status)}
                        >
                          {trial.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="p-3">
                        <p className="text-sm">
                          {new Date(trial.created_at).toLocaleDateString()}
                        </p>
                      </td>
                      <td className="p-3">
                        <Link 
                          to={`/analytics?trial=${trial.id}`}
                          className="btn"
                          data-variant="outline"
                          data-size="sm"
                        >
                          View Analytics
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompanyDashboardPage;
