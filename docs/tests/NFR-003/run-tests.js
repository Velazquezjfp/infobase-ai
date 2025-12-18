/**
 * NFR-003 Test Runner (Node.js compatible)
 * Simulates localStorage functionality and runs tests
 */

// Mock localStorage for Node.js environment
class LocalStorageMock {
  constructor() {
    this.store = {};
  }

  getItem(key) {
    return this.store[key] || null;
  }

  setItem(key, value) {
    this.store[key] = String(value);
  }

  removeItem(key) {
    delete this.store[key];
  }

  clear() {
    this.store = {};
  }

  get length() {
    return Object.keys(this.store).length;
  }

  key(index) {
    const keys = Object.keys(this.store);
    return keys[index] || null;
  }

  hasOwnProperty(key) {
    return key in this.store;
  }
}

// Set up global localStorage
global.localStorage = new LocalStorageMock();
global.performance = { now: () => Date.now() };

// Storage utility functions (inline for testing)
const STORAGE_LIMIT = 5 * 1024 * 1024;
const WARNING_THRESHOLD = 4.5 * 1024 * 1024;
const CRITICAL_THRESHOLD = 4.9 * 1024 * 1024;

function isLocalStorageAvailable() {
  try {
    const test = '__localStorage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch (e) {
    return false;
  }
}

function estimateStorageSize() {
  let total = 0;
  try {
    for (let key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        const value = localStorage.getItem(key);
        if (value) {
          total += (key.length + value.length) * 2;
        }
      }
    }
  } catch (e) {
    console.warn('Error estimating storage size:', e);
  }
  return total;
}

function checkQuota() {
  const used = estimateStorageSize();
  const available = STORAGE_LIMIT;
  const percentage = (used / available) * 100;
  return { used, available, percentage: Math.min(percentage, 100) };
}

function saveToLocalStorage(key, data) {
  if (!isLocalStorageAvailable()) {
    return { success: false, error: 'localStorage is not available' };
  }

  try {
    const serialized = JSON.stringify(data);
    const quota = checkQuota();
    const estimatedNewSize = quota.used + (key.length + serialized.length) * 2;

    if (estimatedNewSize > CRITICAL_THRESHOLD) {
      return {
        success: false,
        error: `Storage limit reached (${quota.percentage.toFixed(1)}%). Cannot save data.`
      };
    }

    localStorage.setItem(key, serialized);

    const finalQuota = checkQuota();
    if (finalQuota.used > WARNING_THRESHOLD && finalQuota.used <= CRITICAL_THRESHOLD) {
      return {
        success: true,
        warning: `Storage usage is high (${finalQuota.percentage.toFixed(1)}%).`
      };
    }

    return { success: true };
  } catch (e) {
    if (e.name === 'QuotaExceededError' || e.code === 22) {
      return { success: false, error: 'Storage quota exceeded' };
    }
    return { success: false, error: e.message || 'Unknown error' };
  }
}

function loadFromLocalStorage(key) {
  if (!isLocalStorageAvailable()) {
    return null;
  }

  try {
    const item = localStorage.getItem(key);
    if (item === null) return null;
    return JSON.parse(item);
  } catch (e) {
    if (e instanceof SyntaxError) {
      console.error(`Malformed JSON in localStorage key "${key}"`);
      localStorage.removeItem(key);
      return null;
    }
    return null;
  }
}

function clearLocalStorage(key) {
  if (!isLocalStorageAvailable()) return false;
  try {
    localStorage.removeItem(key);
    return true;
  } catch (e) {
    return false;
  }
}

// Test execution
const tests = [];
let passCount = 0;
let failCount = 0;

function runTest(testId, testName, testType, testFn) {
  const start = Date.now();
  const timestamp = new Date().toISOString();
  let status = 'passed';
  let errorMessage = undefined;
  let stackTrace = undefined;

  try {
    testFn();
  } catch (error) {
    status = 'failed';
    errorMessage = error.message || String(error);
    stackTrace = error.stack;
  }

  const executionTime = (Date.now() - start) / 1000;

  const result = {
    testId,
    testName,
    testType,
    status,
    executionTime,
    timestamp,
    errorMessage,
    stackTrace
  };

  tests.push(result);

  if (status === 'passed') {
    passCount++;
    console.log(`✓ ${testId}: ${testName} (${executionTime.toFixed(3)}s)`);
  } else {
    failCount++;
    console.log(`✗ ${testId}: ${testName}`);
    console.log(`  Error: ${errorMessage}`);
  }

  return result;
}

console.log('=== NFR-003 LocalStorage Test Suite ===\n');
console.log('Starting test execution...\n');

// TC-NFR-003-01: Basic Save/Load
runTest('TC-NFR-003-01', 'Basic Save/Load', 'unit', () => {
  const testData = { id: 'test1', value: 'Hello World', timestamp: Date.now() };
  const result = saveToLocalStorage('bamf_test_basic', testData);

  if (!result.success) {
    throw new Error(`Save failed: ${result.error}`);
  }

  const loaded = loadFromLocalStorage('bamf_test_basic');
  if (JSON.stringify(loaded) !== JSON.stringify(testData)) {
    throw new Error('Loaded data does not match saved data');
  }

  clearLocalStorage('bamf_test_basic');
});

// TC-NFR-003-02: Fallback to Defaults
runTest('TC-NFR-003-02', 'Fallback to Defaults', 'integration', () => {
  clearLocalStorage('bamf_form_fields_nonexistent');
  const loaded = loadFromLocalStorage('bamf_form_fields_nonexistent');

  if (loaded !== null) {
    throw new Error('Should return null for non-existent key');
  }
});

// TC-NFR-003-03: Storage Quota Check
runTest('TC-NFR-003-03', 'Storage Quota Check', 'unit', () => {
  const quota = checkQuota();

  if (typeof quota.used !== 'number' || quota.used < 0) {
    throw new Error('Invalid quota.used value');
  }

  if (typeof quota.available !== 'number' || quota.available <= 0) {
    throw new Error('Invalid quota.available value');
  }

  if (typeof quota.percentage !== 'number' || quota.percentage < 0 || quota.percentage > 100) {
    throw new Error('Invalid quota.percentage value');
  }
});

// TC-NFR-003-04: Malformed JSON Handling
runTest('TC-NFR-003-04', 'Malformed JSON Handling', 'integration', () => {
  localStorage.setItem('bamf_corrupt_test', '{invalid json}');
  const loaded = loadFromLocalStorage('bamf_corrupt_test');

  if (loaded !== null) {
    throw new Error('Should return null for malformed JSON');
  }

  const stillExists = localStorage.getItem('bamf_corrupt_test');
  if (stillExists !== null) {
    throw new Error('Corrupted data should be auto-cleared');
  }
});

// TC-NFR-003-05: Form Fields Persistence
runTest('TC-NFR-003-05', 'Form Fields Persistence', 'integration', () => {
  const formFields = [
    { id: 'fullName', label: 'Full Name', type: 'text', value: 'John Doe', required: true },
    { id: 'birthDate', label: 'Birth Date', type: 'date', value: '1990-05-15', required: true },
    { id: 'country', label: 'Country', type: 'text', value: 'Afghanistan', required: true }
  ];

  const result = saveToLocalStorage('bamf_form_fields', formFields);
  if (!result.success) {
    throw new Error(`Save failed: ${result.error}`);
  }

  const loaded = loadFromLocalStorage('bamf_form_fields');
  if (!loaded || loaded.length !== 3) {
    throw new Error('Form fields not loaded correctly');
  }

  if (loaded[0].value !== 'John Doe') {
    throw new Error('Form field value not preserved');
  }

  clearLocalStorage('bamf_form_fields');
});

// TC-NFR-003-06: Case Form Data Persistence
runTest('TC-NFR-003-06', 'Case Form Data Persistence', 'integration', () => {
  const caseFormData = {
    'ACTE-2024-001': [
      { id: 'fullName', label: 'Full Name', type: 'text', value: 'Ahmad Ali', required: true }
    ],
    'ACTE-2024-002': [
      { id: 'fullName', label: 'Full Name', type: 'text', value: 'Maria Schmidt', required: true }
    ]
  };

  const result = saveToLocalStorage('bamf_case_form_data', caseFormData);
  if (!result.success) {
    throw new Error(`Save failed: ${result.error}`);
  }

  const loaded = loadFromLocalStorage('bamf_case_form_data');
  if (!loaded || !loaded['ACTE-2024-001']) {
    throw new Error('Case form data not loaded correctly');
  }

  if (loaded['ACTE-2024-001'][0].value !== 'Ahmad Ali') {
    throw new Error('Case-specific form data not preserved');
  }

  clearLocalStorage('bamf_case_form_data');
});

// TC-NFR-003-07: Key Naming Convention
runTest('TC-NFR-003-DATA01', 'Key Naming Convention', 'unit', () => {
  saveToLocalStorage('bamf_test_naming', { test: true });

  let found = false;
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key === 'bamf_test_naming') {
      found = true;
    }
    if (key && !key.startsWith('bamf_')) {
      throw new Error(`Key "${key}" does not follow bamf_ prefix convention`);
    }
  }

  if (!found) {
    throw new Error('Test key not found');
  }

  clearLocalStorage('bamf_test_naming');
});

// TC-NFR-003-E01: LocalStorage Availability
runTest('TC-NFR-003-E01', 'LocalStorage Availability', 'edge-case', () => {
  const isAvailable = isLocalStorageAvailable();

  if (typeof isAvailable !== 'boolean') {
    throw new Error('isLocalStorageAvailable should return boolean');
  }

  if (!isAvailable) {
    throw new Error('LocalStorage should be available');
  }
});

// Print summary
console.log('\n=== Test Summary ===');
console.log(`Total Tests: ${tests.length}`);
console.log(`Passed: ${passCount}`);
console.log(`Failed: ${failCount}`);
console.log(`Success Rate: ${((passCount / tests.length) * 100).toFixed(1)}%\n`);

// Output JSON for test-results.json
const output = {
  requirementId: 'NFR-003',
  executionTimestamp: new Date().toISOString(),
  summary: {
    total: tests.length,
    passed: passCount,
    failed: failCount,
    skipped: 0,
    manual: 0
  },
  testCases: tests
};

console.log('=== JSON Output ===');
console.log(JSON.stringify(output, null, 2));

// Exit with appropriate code
process.exit(failCount > 0 ? 1 : 0);
