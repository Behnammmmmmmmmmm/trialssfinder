import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useStore';
import { trialsAPI } from '../api/trials';
import { Industry } from '../types';

export const UserProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [favorites, setFavorites] = useState<any[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [localSelectedIndustries, setLocalSelectedIndustries] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [favResponse, indResponse, userIndResponse] = await Promise.all([
        trialsAPI.getFavorites(),
        trialsAPI.getIndustries(),
        trialsAPI.getUserIndustries()
      ]);
      
      setFavorites(favResponse.data);
      setIndustries(indResponse.data);
      
      const userIndustryIds = userIndResponse.data.map((ui: any) => ui.industry.id);
      setLocalSelectedIndustries(userIndustryIds);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleIndustryChange = (industryId: number) => {
    setLocalSelectedIndustries(prev =>
      prev.includes(industryId)
        ? prev.filter(id => id !== industryId)
        : [...prev, industryId]
    );
  };

  const saveIndustries = async () => {
    setSaving(true);
    try {
      await trialsAPI.followIndustries(localSelectedIndustries);
      alert('Industries updated successfully! You will receive notifications for new trials in these industries.');
    } catch (error) {
      console.error('Failed to update industries:', error);
      alert('Failed to update industries. Please try again.');
    } finally {
      setSaving(false);
    }
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
      <h1 className="text-3xl font-bold mb-8">My Profile</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <div className="card">
            <div className="card-body">
              <h2 className="text-xl font-semibold mb-4">Account Information</h2>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-muted">Username</p>
                  <p className="font-medium">{user?.username}</p>
                </div>
                <div>
                  <p className="text-sm text-muted">Email</p>
                  <p className="font-medium">{user?.email}</p>
                </div>
                <div>
                  <p className="text-sm text-muted">Account Type</p>
                  <p className="font-medium capitalize">{user?.user_type}</p>
                </div>
                <div>
                  <p className="text-sm text-muted">Email Verified</p>
                  <p className="font-medium">
                    {user?.email_verified ? (
                      <span className="text-success">✓ Verified</span>
                    ) : (
                      <span className="text-warning">⚠ Not Verified</span>
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-2">
          <div className="card mb-8">
            <div className="card-header">
              <h2 className="text-xl font-semibold">Follow Industries</h2>
              <p className="text-sm text-muted mt-1">
                Get notified when new trials are posted in these industries
              </p>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
                {industries.map((industry: Industry) => (
                  <label key={industry.id} className="form-check">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      checked={localSelectedIndustries.includes(industry.id)}
                      onChange={() => handleIndustryChange(industry.id)}
                    />
                    <span className="form-check-label">{industry.name}</span>
                  </label>
                ))}
              </div>
              <button 
                onClick={saveIndustries}
                className="btn" 
                data-variant="primary"
                disabled={saving}
              >
                {saving ? (
                  <span className="flex items-center">
                    <span className="spinner mr-2"></span>
                    Saving...
                  </span>
                ) : (
                  'Save Industry Preferences'
                )}
              </button>
            </div>
          </div>
          
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold">Favorite Trials</h2>
            </div>
            <div className="card-body">
              {favorites.length === 0 ? (
                <p className="text-muted text-center py-8">
                  No favorite trials yet. Start exploring to add favorites!
                </p>
              ) : (
                <div className="space-y-4">
                  {favorites.map(fav => (
                    <div key={fav.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <h3 className="text-lg font-semibold mb-2">{fav.trial.title}</h3>
                      <p className="text-muted mb-3">{fav.trial.description}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted">
                          Added {new Date(fav.created_at).toLocaleDateString()}
                        </span>
                        <a 
                          href={`/trials/${fav.trial.id}`} 
                          className="btn" 
                          data-variant="outline"
                          data-size="sm"
                        >
                          View Details
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfilePage;
