// Test helper: initialize i18next exactly the way src/i18n/config.ts does
// (minus the browser LanguageDetector and react-i18next plumbing — neither
// affects the t() lookup behavior we are testing) and print t(key).
//
// Usage: node _i18next_runner.mjs <language> <key> <de.json> <en.json>
//
// Exits 0 on success and prints the resolved translation on stdout.
// Any i18next console.error messages are forwarded on stderr; tests assert on
// the absence of those for the missing-everywhere fallback case.
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const __dirname = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);

const projectRoot = resolve(__dirname, '..', '..', '..');
const i18nextModule = require(resolve(projectRoot, 'node_modules/i18next/dist/cjs/i18next.js'));
// CJS build exports the singleton instance directly (no .default wrapper).
const i18next = i18nextModule.default ?? i18nextModule;

const [, , language, key, dePath, enPath] = process.argv;
if (!language || !key || !dePath || !enPath) {
  console.error('usage: node _i18next_runner.mjs <language> <key> <de.json> <en.json>');
  process.exit(2);
}

const de = JSON.parse(readFileSync(dePath, 'utf8'));
const en = JSON.parse(readFileSync(enPath, 'utf8'));

await i18next.init({
  resources: {
    de: { translation: de },
    en: { translation: en },
  },
  // Mirror src/i18n/config.ts production options:
  fallbackLng: 'de',
  lng: language,
  debug: false,
  returnNull: false,
  parseMissingKeyHandler: (k) => k,
  interpolation: { escapeValue: false },
});

const value = i18next.t(key);
process.stdout.write(String(value));
