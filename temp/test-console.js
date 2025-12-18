/**
 * NFR-003 Browser Console Test Script
 *
 * Copy and paste this into your browser console while the app is running
 * to test localStorage functionality interactively.
 */

// Test 1: Check if BAMF keys exist
console.log('=== TEST 1: Check BAMF localStorage Keys ===');
const bamfKeys = [];
for (let i = 0; i < localStorage.length; i++) {
  const key = localStorage.key(i);
  if (key && key.startsWith('bamf_')) {
    bamfKeys.push(key);
  }
}
console.log(`Found ${bamfKeys.length} BAMF keys:`, bamfKeys);

// Test 2: View form fields
console.log('\n=== TEST 2: View Form Fields ===');
const formFields = localStorage.getItem('bamf_form_fields');
if (formFields) {
  try {
    const parsed = JSON.parse(formFields);
    console.log(`Form fields count: ${parsed.length}`);
    console.log('Form fields:', parsed);
  } catch (e) {
    console.error('Error parsing form fields:', e);
  }
} else {
  console.log('No form fields found in localStorage yet');
}

// Test 3: View case form data
console.log('\n=== TEST 3: View Case Form Data ===');
const caseFormData = localStorage.getItem('bamf_case_form_data');
if (caseFormData) {
  try {
    const parsed = JSON.parse(caseFormData);
    const caseIds = Object.keys(parsed);
    console.log(`Cases with form data: ${caseIds.length}`);
    console.log('Case IDs:', caseIds);
    console.log('Case form data:', parsed);
  } catch (e) {
    console.error('Error parsing case form data:', e);
  }
} else {
  console.log('No case form data found in localStorage yet');
}

// Test 4: Calculate storage usage
console.log('\n=== TEST 4: Storage Usage ===');
let totalSize = 0;
let bamfSize = 0;

for (let key in localStorage) {
  if (localStorage.hasOwnProperty(key)) {
    const value = localStorage.getItem(key);
    if (value) {
      const size = (key.length + value.length) * 2; // UTF-16
      totalSize += size;
      if (key.startsWith('bamf_')) {
        bamfSize += size;
        console.log(`  ${key}: ${(size / 1024).toFixed(2)} KB`);
      }
    }
  }
}

const totalKB = totalSize / 1024;
const totalMB = totalKB / 1024;
const bamfKB = bamfSize / 1024;
const percentage = (totalSize / (5 * 1024 * 1024)) * 100;

console.log(`\nTotal Storage: ${totalKB.toFixed(2)} KB (${totalMB.toFixed(2)} MB)`);
console.log(`BAMF Storage: ${bamfKB.toFixed(2)} KB`);
console.log(`Usage: ${percentage.toFixed(1)}% of ~5MB limit`);

if (percentage > 90) {
  console.warn('⚠️ WARNING: Storage usage is high!');
} else if (percentage > 80) {
  console.warn('⚠️ CAUTION: Approaching storage limit');
} else {
  console.log('✅ Storage usage is healthy');
}

// Test 5: Test data integrity
console.log('\n=== TEST 5: Data Integrity Check ===');
let integrityPass = true;

if (formFields) {
  try {
    const parsed = JSON.parse(formFields);
    if (!Array.isArray(parsed)) {
      console.error('❌ Form fields is not an array');
      integrityPass = false;
    } else {
      console.log('✅ Form fields structure valid');
    }
  } catch (e) {
    console.error('❌ Form fields JSON is corrupted');
    integrityPass = false;
  }
}

if (caseFormData) {
  try {
    const parsed = JSON.parse(caseFormData);
    if (typeof parsed !== 'object' || Array.isArray(parsed)) {
      console.error('❌ Case form data is not an object');
      integrityPass = false;
    } else {
      console.log('✅ Case form data structure valid');
    }
  } catch (e) {
    console.error('❌ Case form data JSON is corrupted');
    integrityPass = false;
  }
}

if (integrityPass) {
  console.log('\n✅ All data integrity checks passed!');
} else {
  console.warn('\n⚠️ Some data integrity issues detected');
}

// Utility functions
console.log('\n=== Available Utility Functions ===');
console.log('Run these commands to interact with localStorage:');
console.log('');
console.log('// View specific field data');
console.log('JSON.parse(localStorage.getItem("bamf_form_fields"))');
console.log('');
console.log('// Clear all BAMF data (CAUTION!)');
console.log('for (let k in localStorage) { if (k.startsWith("bamf_")) localStorage.removeItem(k); }');
console.log('');
console.log('// Export BAMF data');
console.log('const backup = {}; for (let k in localStorage) { if (k.startsWith("bamf_")) backup[k] = localStorage.getItem(k); } console.log(JSON.stringify(backup, null, 2));');
console.log('');
console.log('// Re-run this test');
console.log('// Just paste this script again!');

console.log('\n=== Test Complete ===');
console.log('Check the results above for any issues.');
