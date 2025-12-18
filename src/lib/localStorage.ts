/**
 * LocalStorage Utility Module for BAMF Case Management System
 *
 * Provides safe localStorage operations with error handling, quota checking,
 * and graceful fallbacks. All keys use "bamf_" prefix to avoid conflicts.
 *
 * @module localStorage
 */

/**
 * Storage quota information
 */
export interface StorageQuota {
  used: number;        // Bytes used
  available: number;   // Total bytes available (estimated)
  percentage: number;  // Percentage used (0-100)
}

/**
 * Result of a save operation
 */
export interface SaveResult {
  success: boolean;
  error?: string;
  warning?: string;
}

// Storage limits (conservative estimates)
const STORAGE_LIMIT = 5 * 1024 * 1024; // 5MB typical browser limit
const WARNING_THRESHOLD = 4.5 * 1024 * 1024; // 4.5MB - warn user
const CRITICAL_THRESHOLD = 4.9 * 1024 * 1024; // 4.9MB - prevent save

/**
 * Check if localStorage is available in the current browser
 * Handles cases like private browsing where localStorage may be disabled
 */
export function isLocalStorageAvailable(): boolean {
  try {
    const test = '__localStorage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Estimate the size of all data in localStorage
 * Returns size in bytes
 */
function estimateStorageSize(): number {
  let total = 0;

  try {
    for (let key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        const value = localStorage.getItem(key);
        if (value) {
          // Estimate: key length + value length * 2 (UTF-16 encoding)
          total += (key.length + value.length) * 2;
        }
      }
    }
  } catch (e) {
    console.warn('Error estimating storage size:', e);
  }

  return total;
}

/**
 * Check current localStorage quota usage
 * Returns quota information including used space and percentage
 */
export function checkQuota(): StorageQuota {
  const used = estimateStorageSize();
  const available = STORAGE_LIMIT;
  const percentage = (used / available) * 100;

  return {
    used,
    available,
    percentage: Math.min(percentage, 100), // Cap at 100%
  };
}

/**
 * Save data to localStorage with error handling and quota checking
 *
 * @param key - Storage key (will be used as-is, should include "bamf_" prefix)
 * @param data - Data to store (will be JSON serialized)
 * @returns SaveResult with success status and any warnings/errors
 *
 * @example
 * const result = saveToLocalStorage('bamf_form_fields', formFields);
 * if (!result.success) {
 *   console.error(result.error);
 * }
 */
export function saveToLocalStorage(key: string, data: any): SaveResult {
  // Check if localStorage is available
  if (!isLocalStorageAvailable()) {
    return {
      success: false,
      error: 'localStorage is not available. Changes will not persist across sessions.',
    };
  }

  try {
    // Serialize data
    const serialized = JSON.stringify(data);

    // Check quota before saving
    const quota = checkQuota();
    const estimatedNewSize = quota.used + (key.length + serialized.length) * 2;

    // Prevent save if over critical threshold
    if (estimatedNewSize > CRITICAL_THRESHOLD) {
      return {
        success: false,
        error: `Storage limit reached (${(quota.percentage).toFixed(1)}%). Cannot save data. Please remove unused items.`,
      };
    }

    // Save to localStorage
    localStorage.setItem(key, serialized);

    // Check if we should warn about approaching limit
    const finalQuota = checkQuota();
    if (finalQuota.used > WARNING_THRESHOLD && finalQuota.used <= CRITICAL_THRESHOLD) {
      return {
        success: true,
        warning: `Storage usage is high (${finalQuota.percentage.toFixed(1)}%). Consider removing unused data.`,
      };
    }

    return { success: true };

  } catch (e: any) {
    // Handle QuotaExceededError
    if (e.name === 'QuotaExceededError' || e.code === 22) {
      return {
        success: false,
        error: 'Storage quota exceeded. Please remove some data to free up space.',
      };
    }

    // Handle other errors
    console.error('Error saving to localStorage:', e);
    return {
      success: false,
      error: `Failed to save data: ${e.message || 'Unknown error'}`,
    };
  }
}

/**
 * Load data from localStorage with error handling
 *
 * @param key - Storage key to retrieve
 * @returns Parsed data or null if not found or error occurred
 *
 * @example
 * const formFields = loadFromLocalStorage<FormField[]>('bamf_form_fields');
 * if (!formFields) {
 *   // Use default values
 * }
 */
export function loadFromLocalStorage<T>(key: string): T | null {
  // Check if localStorage is available
  if (!isLocalStorageAvailable()) {
    console.warn('localStorage is not available');
    return null;
  }

  try {
    const item = localStorage.getItem(key);

    // Return null if key doesn't exist
    if (item === null) {
      return null;
    }

    // Parse and return data
    return JSON.parse(item) as T;

  } catch (e: any) {
    // Handle JSON parse errors
    if (e instanceof SyntaxError) {
      console.error(`Malformed JSON in localStorage key "${key}":`, e);
      console.warn(`Clearing corrupted data for key: ${key}`);
      // Clear corrupted data
      try {
        localStorage.removeItem(key);
      } catch (clearError) {
        console.error('Failed to clear corrupted data:', clearError);
      }
      return null;
    }

    // Handle other errors
    console.error(`Error loading from localStorage (key: ${key}):`, e);
    return null;
  }
}

/**
 * Remove a specific key from localStorage
 *
 * @param key - Storage key to remove
 * @returns true if successful, false otherwise
 */
export function clearLocalStorage(key: string): boolean {
  if (!isLocalStorageAvailable()) {
    console.warn('localStorage is not available');
    return false;
  }

  try {
    localStorage.removeItem(key);
    return true;
  } catch (e) {
    console.error(`Error removing localStorage key "${key}":`, e);
    return false;
  }
}

/**
 * Clear all BAMF-related localStorage keys
 * Useful for testing or complete reset
 *
 * @returns Number of keys cleared
 */
export function clearAllBamfStorage(): number {
  if (!isLocalStorageAvailable()) {
    console.warn('localStorage is not available');
    return 0;
  }

  let cleared = 0;

  try {
    const keysToRemove: string[] = [];

    // Find all keys with bamf_ prefix
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('bamf_')) {
        keysToRemove.push(key);
      }
    }

    // Remove all found keys
    keysToRemove.forEach(key => {
      localStorage.removeItem(key);
      cleared++;
    });

    console.log(`Cleared ${cleared} BAMF storage keys`);
    return cleared;

  } catch (e) {
    console.error('Error clearing BAMF storage:', e);
    return cleared;
  }
}

/**
 * Get all BAMF storage keys and their sizes
 * Useful for debugging and monitoring
 */
export function getBamfStorageInfo(): Record<string, number> {
  const info: Record<string, number> = {};

  if (!isLocalStorageAvailable()) {
    return info;
  }

  try {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('bamf_')) {
        const value = localStorage.getItem(key);
        if (value) {
          // Size in bytes (UTF-16)
          info[key] = (key.length + value.length) * 2;
        }
      }
    }
  } catch (e) {
    console.error('Error getting BAMF storage info:', e);
  }

  return info;
}

/**
 * Export localStorage data for backup
 * Returns all BAMF data as JSON string
 */
export function exportBamfStorage(): string | null {
  if (!isLocalStorageAvailable()) {
    return null;
  }

  try {
    const data: Record<string, any> = {};

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('bamf_')) {
        const value = localStorage.getItem(key);
        if (value) {
          try {
            data[key] = JSON.parse(value);
          } catch {
            data[key] = value; // Store as string if not valid JSON
          }
        }
      }
    }

    return JSON.stringify(data, null, 2);
  } catch (e) {
    console.error('Error exporting BAMF storage:', e);
    return null;
  }
}

/**
 * Import localStorage data from backup
 *
 * @param jsonData - JSON string containing backup data
 * @returns Number of keys imported
 */
export function importBamfStorage(jsonData: string): number {
  if (!isLocalStorageAvailable()) {
    console.warn('localStorage is not available');
    return 0;
  }

  try {
    const data = JSON.parse(jsonData);
    let imported = 0;

    for (const key in data) {
      if (key.startsWith('bamf_')) {
        const value = typeof data[key] === 'string' ? data[key] : JSON.stringify(data[key]);
        localStorage.setItem(key, value);
        imported++;
      }
    }

    console.log(`Imported ${imported} BAMF storage keys`);
    return imported;
  } catch (e) {
    console.error('Error importing BAMF storage:', e);
    return 0;
  }
}
