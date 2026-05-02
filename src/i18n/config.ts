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
    // Never return null for missing keys.
    // S001-F-010: respect the call site's defaultValue. When `t('ns.key', 'Friendly Label')`
    // hits a missing key, return 'Friendly Label' so the UI shows graceful fallbacks
    // instead of leaking the raw `ns.key` string (the leak symptoms reported by the
    // operator: `formFields.Passnummer`, `documents.renders.translated`, etc.).
    // When `t('ns.key')` is called with NO defaultValue, fall through to the raw key
    // — preserves the dev-debug signal for unguarded t() calls.
    returnNull: false,
    parseMissingKeyHandler: (key: string, defaultValue?: string) => defaultValue ?? key,

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
