#!/usr/bin/env node
// i18n coverage check for the BAMF ACTE Companion frontend.
//
// German is the source of truth for the closed-environment demo. This script
// compares src/i18n/locales/de.json and src/i18n/locales/en.json and:
//   - Prints a warning for every key present in de.json but missing in en.json
//     (English is nice-to-have; the runtime falls back to German).
//   - Exits 1 if any key is present in en.json but missing in de.json
//     (German must always cover the surface).
//
// Usage:
//   node scripts/i18n-coverage.js
//   node scripts/i18n-coverage.js <de.json> <en.json>   # for testing
//
// Requires Node 18+ (uses readFileSync from fs and import.meta.url).
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(__dirname, '..');

const dePath = process.argv[2] ?? resolve(projectRoot, 'src/i18n/locales/de.json');
const enPath = process.argv[3] ?? resolve(projectRoot, 'src/i18n/locales/en.json');

function loadJson(p) {
  try {
    return JSON.parse(readFileSync(p, 'utf8'));
  } catch (err) {
    console.error(`i18n-coverage: failed to read ${p}: ${err.message}`);
    process.exit(2);
  }
}

function flatten(obj, prefix, out) {
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v !== null && typeof v === 'object' && !Array.isArray(v)) {
      flatten(v, key, out);
    } else {
      out.add(key);
    }
  }
  return out;
}

const de = loadJson(dePath);
const en = loadJson(enPath);

const deKeys = flatten(de, '', new Set());
const enKeys = flatten(en, '', new Set());

const missingInEn = [...deKeys].filter((k) => !enKeys.has(k)).sort();
const missingInDe = [...enKeys].filter((k) => !deKeys.has(k)).sort();

for (const key of missingInEn) {
  console.warn(`warning: key "${key}" is present in de.json but missing in en.json`);
}

if (missingInDe.length > 0) {
  for (const key of missingInDe) {
    console.error(`error: key "${key}" is present in en.json but missing in de.json (German is required)`);
  }
  console.error(`i18n-coverage: ${missingInDe.length} key(s) missing in de.json (German is the source of truth)`);
  process.exit(1);
}

if (missingInEn.length > 0) {
  console.warn(`i18n-coverage: ${missingInEn.length} key(s) missing in en.json (warning only — runtime falls back to German)`);
} else {
  console.log('i18n-coverage: locale files are in sync.');
}

process.exit(0);
