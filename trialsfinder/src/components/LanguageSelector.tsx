import React from 'react';

import { SUPPORTED_LANGUAGES } from '../i18n/config';
import { useTranslation } from '../i18n';

export const LanguageSelector: React.FC = () => {
  const { i18n } = useTranslation();
  
  const handleChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const lang = e.target.value;
    await i18n.changeLanguage(lang);
    
    // Update HTML dir attribute
    document.documentElement.dir = SUPPORTED_LANGUAGES[lang as keyof typeof SUPPORTED_LANGUAGES].dir;
    
    // Update lang attribute
    document.documentElement.lang = lang;
    
    // Update backend language preference
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      void fetch('/api/auth/language/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ language: lang }),
      });
    }
  };
  
  return (
    <div className="language-selector">
      <label htmlFor="language-select" className="sr-only">
        Choose language
      </label>
      <select 
        id="language-select"
        value={i18n.language} 
        onChange={handleChange}
        className="form-select"
        aria-label="Select language"
      >
        {(Object.entries(SUPPORTED_LANGUAGES) as [string, { name: string; dir: string }][]).map(([code, { name }]) => (
          <option key={code} value={code}>{name}</option>
        ))}
      </select>
    </div>
  );
};