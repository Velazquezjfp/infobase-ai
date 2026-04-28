import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import de from './locales/de.json';
import en from './locales/en.json';

const resources = {
  de: {
    translation: de
  },
  en: {
    translation: en
  }
};

i18n
  // Detect user language
  .use(LanguageDetector)
  // Pass the i18n instance to react-i18next
  .use(initReactI18next)
  // Initialize i18next
  .init({
    resources,
    // German is the source of truth; missing en keys fall back to de.
    fallbackLng: 'de',
    lng: 'de', // Default language
    debug: import.meta.env.DEV,
    // Never return null for missing keys; render the key string instead so
    // developers can spot it without crashing the UI.
    returnNull: false,
    parseMissingKeyHandler: (key: string) => key,

    // Language detector options
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'bamf_language'
    },

    interpolation: {
      escapeValue: false // React already escapes values
    }
  });

export default i18n;
