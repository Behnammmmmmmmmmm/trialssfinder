import React, { useState } from 'react';
import { useTranslation } from '../i18n';

export const PrivacyDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [consents, setConsents] = useState({
    necessary: true,
    functional: true,
    analytics: false,
    marketing: false,
  });

  const handleExportData = async () => {
    try {
      const response = await fetch('/api/compliance/export-data/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        alert(t('privacy.exportRequested'));
      }
    } catch (error) {
      console.error('Failed to request data export:', error);
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm(t('privacy.deleteConfirm'))) {
      return;
    }

    try {
      const response = await fetch('/api/compliance/delete-account/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        alert(t('privacy.deletionRequested'));
      }
    } catch (error) {
      console.error('Failed to request account deletion:', error);
    }
  };

  const updateConsents = async () => {
    try {
      const response = await fetch('/api/compliance/consent/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ consents }),
      });
      
      if (response.ok) {
        alert('Consent preferences updated');
      }
    } catch (error) {
      console.error('Failed to update consents:', error);
    }
  };

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">{t('privacy.title')}</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold">{t('privacy.yourConsents')}</h2>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <label className="form-check">
                <input
                  type="checkbox"
                  className="form-check-input"
                  checked={consents.necessary}
                  disabled
                />
                <span className="form-check-label">{t('cookies.necessary')}</span>
              </label>
              
              <label className="form-check">
                <input
                  type="checkbox"
                  className="form-check-input"
                  checked={consents.functional}
                  onChange={(e) => setConsents({...consents, functional: e.target.checked})}
                />
                <span className="form-check-label">{t('cookies.functional')}</span>
              </label>
              
              <label className="form-check">
                <input
                  type="checkbox"
                  className="form-check-input"
                  checked={consents.analytics}
                  onChange={(e) => setConsents({...consents, analytics: e.target.checked})}
                />
                <span className="form-check-label">{t('cookies.analytics')}</span>
              </label>
              
              <label className="form-check">
                <input
                  type="checkbox"
                  className="form-check-input"
                  checked={consents.marketing}
                  onChange={(e) => setConsents({...consents, marketing: e.target.checked})}
                />
                <span className="form-check-label">{t('cookies.marketing')}</span>
              </label>
            </div>
            
            <button 
              onClick={updateConsents}
              className="btn mt-6" 
              data-variant="primary"
            >
              Update Preferences
            </button>
          </div>
        </div>
        
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold">{t('privacy.yourRights')}</h2>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Data Export</h3>
                <p className="text-sm text-muted mb-3">
                  Download all your personal data in a machine-readable format.
                </p>
                <button 
                  onClick={handleExportData}
                  className="btn" 
                  data-variant="outline"
                >
                  {t('privacy.exportData')}
                </button>
              </div>
              
              <hr />
              
              <div>
                <h3 className="font-semibold mb-2">Account Deletion</h3>
                <p className="text-sm text-muted mb-3">
                  Permanently delete your account and all associated data.
                </p>
                <button 
                  onClick={handleDeleteAccount}
                  className="btn" 
                  data-variant="danger"
                >
                  {t('privacy.deleteAccount')}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyDashboard;