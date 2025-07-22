import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

export const SUPPORTED_LANGUAGES = {
  en: { name: 'English', dir: 'ltr' },
  es: { name: 'Español', dir: 'ltr' },
  fr: { name: 'Français', dir: 'ltr' },
  de: { name: 'Deutsch', dir: 'ltr' },
  ar: { name: 'العربية', dir: 'rtl' },
  he: { name: 'עברית', dir: 'rtl' },
};

// Custom backend that uses native fetch
const customBackend = {
  type: 'backend' as const,
  init: function() {},
  read: function(language: string, namespace: string, callback: Function) {
    const loadPath = `/locales/${language}/${namespace}.json`;
    
    fetch(loadPath)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Failed to load ${loadPath}`);
        }
        return response.json();
      })
      .then(data => {
        callback(null, data);
      })
      .catch(error => {
        callback(error, null);
      });
  }
};

void i18n
  .use(customBackend as any)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    
    interpolation: {
      escapeValue: false,
    },
    
    detection: {
      order: ['cookie', 'localStorage', 'navigator', 'htmlTag'],
      caches: ['cookie', 'localStorage'],
    },
    
    react: {
      useSuspense: false,
    },
  });

export default i18n;