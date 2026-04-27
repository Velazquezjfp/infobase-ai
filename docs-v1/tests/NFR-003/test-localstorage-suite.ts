/**
 * NFR-003 LocalStorage Test Suite
 * Comprehensive automated tests for localStorage functionality
 */

import {
  saveToLocalStorage,
  loadFromLocalStorage,
  clearLocalStorage,
  checkQuota,
  isLocalStorageAvailable,
  clearAllBamfStorage,
  getBamfStorageInfo,
  exportBamfStorage,
  importBamfStorage,
  StorageQuota,
  SaveResult
} from '../../../src/lib/localStorage';

interface TestResult {
  testId: string;
  testName: string;
  testType: 'unit' | 'integration' | 'edge-case';
  status: 'passed' | 'failed' | 'skipped';
  executionTime: number;
  timestamp: string;
  errorMessage?: string;
  stackTrace?: string;
}

class LocalStorageTestSuite {
  private results: TestResult[] = [];
  private startTime: number = 0;

  constructor() {
    this.results = [];
  }

  private recordTest(
    testId: string,
    testName: string,
    testType: 'unit' | 'integration' | 'edge-case',
    testFn: () => void | Promise<void>
  ): TestResult {
    const start = performance.now();
    const timestamp = new Date().toISOString();
    let status: 'passed' | 'failed' = 'passed';
    let errorMessage: string | undefined;
    let stackTrace: string | undefined;

    try {
      const result = testFn();
      if (result instanceof Promise) {
        throw new Error('Async tests not supported in this runner');
      }
    } catch (error: any) {
      status = 'failed';
      errorMessage = error.message || String(error);
      stackTrace = error.stack;
    }

    const executionTime = (performance.now() - start) / 1000;

    return {
      testId,
      testName,
      testType,
      status,
      executionTime,
      timestamp,
      errorMessage,
      stackTrace
    };
  }

  // TC-NFR-003-01: Basic Save/Load
  testBasicSaveLoad(): TestResult {
    return this.recordTest(
      'TC-NFR-003-01',
      'Basic Save/Load',
      'unit',
      () => {
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
      }
    );
  }

  // TC-NFR-003-02: Fallback to Defaults
  testFallbackToDefaults(): TestResult {
    return this.recordTest(
      'TC-NFR-003-02',
      'Fallback to Defaults',
      'integration',
      () => {
        clearLocalStorage('bamf_form_fields_nonexistent');
        const loaded = loadFromLocalStorage('bamf_form_fields_nonexistent');

        if (loaded !== null) {
          throw new Error('Should return null for non-existent key');
        }
      }
    );
  }

  // TC-NFR-003-03: Storage Quota Check
  testStorageQuota(): TestResult {
    return this.recordTest(
      'TC-NFR-003-03',
      'Storage Quota Check',
      'unit',
      () => {
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
      }
    );
  }

  // TC-NFR-003-04: Malformed JSON Handling
  testMalformedJSON(): TestResult {
    return this.recordTest(
      'TC-NFR-003-04',
      'Malformed JSON Handling',
      'integration',
      () => {
        // Manually set malformed JSON
        if (typeof localStorage !== 'undefined') {
          localStorage.setItem('bamf_corrupt_test', '{invalid json}');
        }

        const loaded = loadFromLocalStorage('bamf_corrupt_test');

        if (loaded !== null) {
          throw new Error('Should return null for malformed JSON');
        }

        // Verify corrupted data was cleared
        const stillExists = typeof localStorage !== 'undefined'
          ? localStorage.getItem('bamf_corrupt_test')
          : null;

        if (stillExists !== null) {
          throw new Error('Corrupted data should be auto-cleared');
        }
      }
    );
  }

  // TC-NFR-003-05: Form Fields Persistence
  testFormFieldPersistence(): TestResult {
    return this.recordTest(
      'TC-NFR-003-05',
      'Form Fields Persistence',
      'integration',
      () => {
        const formFields = [
          { id: 'fullName', label: 'Full Name', type: 'text', value: 'John Doe', required: true },
          { id: 'birthDate', label: 'Birth Date', type: 'date', value: '1990-05-15', required: true },
          { id: 'country', label: 'Country', type: 'text', value: 'Afghanistan', required: true }
        ];

        const result = saveToLocalStorage('bamf_form_fields', formFields);
        if (!result.success) {
          throw new Error(`Save failed: ${result.error}`);
        }

        const loaded = loadFromLocalStorage<any[]>('bamf_form_fields');
        if (!loaded || loaded.length !== 3) {
          throw new Error('Form fields not loaded correctly');
        }

        if (loaded[0].value !== 'John Doe') {
          throw new Error('Form field value not preserved');
        }

        clearLocalStorage('bamf_form_fields');
      }
    );
  }

  // TC-NFR-003-06: Case Form Data Persistence
  testCaseFormDataPersistence(): TestResult {
    return this.recordTest(
      'TC-NFR-003-06',
      'Case Form Data Persistence',
      'integration',
      () => {
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

        const loaded = loadFromLocalStorage<Record<string, any[]>>('bamf_case_form_data');
        if (!loaded || !loaded['ACTE-2024-001']) {
          throw new Error('Case form data not loaded correctly');
        }

        if (loaded['ACTE-2024-001'][0].value !== 'Ahmad Ali') {
          throw new Error('Case-specific form data not preserved');
        }

        clearLocalStorage('bamf_case_form_data');
      }
    );
  }

  // TC-NFR-003-DATA01: Key Naming Convention
  testKeyNaming(): TestResult {
    return this.recordTest(
      'TC-NFR-003-DATA01',
      'Key Naming Convention',
      'unit',
      () => {
        // Save test data with proper prefix
        saveToLocalStorage('bamf_test_naming', { test: true });

        const info = getBamfStorageInfo();
        let hasBamfKey = false;

        for (const key in info) {
          if (!key.startsWith('bamf_')) {
            throw new Error(`Key "${key}" does not follow bamf_ prefix convention`);
          }
          if (key === 'bamf_test_naming') {
            hasBamfKey = true;
          }
        }

        if (!hasBamfKey) {
          throw new Error('Test key not found in BAMF storage info');
        }

        clearLocalStorage('bamf_test_naming');
      }
    );
  }

  // TC-NFR-003-E01: LocalStorage Availability Check
  testLocalStorageAvailability(): TestResult {
    return this.recordTest(
      'TC-NFR-003-E01',
      'LocalStorage Availability Check',
      'edge-case',
      () => {
        const isAvailable = isLocalStorageAvailable();

        if (typeof isAvailable !== 'boolean') {
          throw new Error('isLocalStorageAvailable should return boolean');
        }

        // In normal browser context, it should be true
        if (typeof localStorage !== 'undefined' && !isAvailable) {
          throw new Error('LocalStorage should be available in this context');
        }
      }
    );
  }

  // TC-NFR-003-E02: Export/Import Functionality
  testExportImport(): TestResult {
    return this.recordTest(
      'TC-NFR-003-E02',
      'Export/Import Functionality',
      'edge-case',
      () => {
        // Save some test data
        saveToLocalStorage('bamf_export_test', { data: 'export_test_value' });

        // Export
        const exported = exportBamfStorage();
        if (!exported) {
          throw new Error('Export failed');
        }

        // Verify export is valid JSON
        const parsed = JSON.parse(exported);
        if (!parsed.bamf_export_test) {
          throw new Error('Exported data does not contain test key');
        }

        // Clear and import
        clearLocalStorage('bamf_export_test');
        const imported = importBamfStorage(exported);

        if (imported === 0) {
          throw new Error('Import failed');
        }

        // Verify imported data
        const loaded = loadFromLocalStorage('bamf_export_test');
        if (!loaded || (loaded as any).data !== 'export_test_value') {
          throw new Error('Imported data not correct');
        }

        clearLocalStorage('bamf_export_test');
      }
    );
  }

  // TC-NFR-003-E03: Clear All BAMF Storage
  testClearAllBamfStorage(): TestResult {
    return this.recordTest(
      'TC-NFR-003-E03',
      'Clear All BAMF Storage',
      'edge-case',
      () => {
        // Add multiple test keys
        saveToLocalStorage('bamf_clear_test_1', { data: 1 });
        saveToLocalStorage('bamf_clear_test_2', { data: 2 });
        saveToLocalStorage('bamf_clear_test_3', { data: 3 });

        // Clear all
        const cleared = clearAllBamfStorage();

        if (cleared < 3) {
          throw new Error(`Expected to clear at least 3 keys, but cleared ${cleared}`);
        }

        // Verify all cleared
        const loaded1 = loadFromLocalStorage('bamf_clear_test_1');
        const loaded2 = loadFromLocalStorage('bamf_clear_test_2');
        const loaded3 = loadFromLocalStorage('bamf_clear_test_3');

        if (loaded1 !== null || loaded2 !== null || loaded3 !== null) {
          throw new Error('Not all BAMF keys were cleared');
        }
      }
    );
  }

  // Run all tests
  runAll(): TestResult[] {
    console.log('=== NFR-003 LocalStorage Test Suite ===\n');
    this.results = [];

    this.results.push(this.testBasicSaveLoad());
    this.results.push(this.testFallbackToDefaults());
    this.results.push(this.testStorageQuota());
    this.results.push(this.testMalformedJSON());
    this.results.push(this.testFormFieldPersistence());
    this.results.push(this.testCaseFormDataPersistence());
    this.results.push(this.testKeyNaming());
    this.results.push(this.testLocalStorageAvailability());
    this.results.push(this.testExportImport());
    this.results.push(this.testClearAllBamfStorage());

    return this.results;
  }

  // Get summary
  getSummary() {
    const total = this.results.length;
    const passed = this.results.filter(r => r.status === 'passed').length;
    const failed = this.results.filter(r => r.status === 'failed').length;
    const skipped = this.results.filter(r => r.status === 'skipped').length;

    return {
      total,
      passed,
      failed,
      skipped,
      successRate: total > 0 ? (passed / total) * 100 : 0
    };
  }

  // Get results
  getResults(): TestResult[] {
    return this.results;
  }
}

// Export for use in other contexts
export { LocalStorageTestSuite, TestResult };

// If running in Node.js/test environment
if (typeof window !== 'undefined') {
  (window as any).LocalStorageTestSuite = LocalStorageTestSuite;
}
