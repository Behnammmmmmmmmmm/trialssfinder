import React, { useState, useEffect } from 'react';

import { useTranslation } from '../i18n';

interface CookiePreferences {
  necessary: boolean;
  functional: boolean;
  analytics: boolean;
  marketing: boolean;
}

export const CookieConsent: React.FC = () => {
  const { t } = useTranslation();
  const [show, setShow] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true,
    functional: true,
    analytics: false,
    marketing: false,
  });
  
  useEffect(() => {
    const consent = localStorage.getItem('cookie_consent');
    if (!consent) {
      setShow(true);
    }
  }, []);
  
  const handleAcceptAll = () => {
    const allAccepted = {
      necessary: true,
      functional: true,
      analytics: true,
      marketing: true,
    };
    savePreferences(allAccepted);
  };
  
  const handleAcceptSelected = () => {
    savePreferences(preferences);
  };
  
  const savePreferences = (prefs: CookiePreferences) => {
    localStorage.setItem('cookie_consent', JSON.stringify(prefs));
    document.cookie = `cookie_consent=${JSON.stringify(prefs)}; path=/; max-age=31536000; SameSite=Lax`;
    setShow(false);
    
    // Initialize analytics based on consent
    if (prefs.analytics) {
      // Initialize analytics tools
      console.log('Analytics initialized');
    }
  };
  
  if (!show) {
    return null;
  }
  
  return (
    <div className="cookie-consent">
      <h3>{t('cookies.title')}</h3>
      <p>{t('cookies.description')}</p>
      
      <div className="cookie-options">
        <label>
          <input
            type="checkbox"
            checked={preferences.necessary}
            disabled
          />
          {t('cookies.necessary')}
        </label>
        
        <label>
          <input
            type="checkbox"
            checked={preferences.functional}
            onChange={(e) => setPreferences({...preferences, functional: e.target.checked})}
          />
          {t('cookies.functional')}
        </label>
        
        <label>
          <input
            type="checkbox"
            checked={preferences.analytics}
            onChange={(e) => setPreferences({...preferences, analytics: e.target.checked})}
          />
          {t('cookies.analytics')}
        </label>
        
        <label>
          <input
            type="checkbox"
            checked={preferences.marketing}
            onChange={(e) => setPreferences({...preferences, marketing: e.target.checked})}
          />
          {t('cookies.marketing')}
        </label>
      </div>
      
      <div className="cookie-actions">
        <button onClick={handleAcceptSelected}>{t('cookies.acceptSelected')}</button>
        <button onClick={handleAcceptAll}>{t('cookies.acceptAll')}</button>
      </div>
    </div>
  );
};