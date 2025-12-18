import { initialFormFields, sampleCaseFormData } from '../mockData';
import { FormField } from '@/types/case';

describe('Case-Type Form Schemas', () => {
  describe('initialFormFields', () => {
    it('has exactly 7 fields', () => {
      expect(initialFormFields).toHaveLength(7);
    });

    it('has correct required fields', () => {
      const requiredFields = initialFormFields.filter(f => f.required);
      expect(requiredFields).toHaveLength(5);

      const requiredIds = requiredFields.map(f => f.id);
      expect(requiredIds).toContain('fullName');
      expect(requiredIds).toContain('birthDate');
      expect(requiredIds).toContain('countryOfOrigin');
      expect(requiredIds).toContain('currentAddress');
      expect(requiredIds).toContain('reasonForApplication');
    });

    it('has all expected field IDs', () => {
      const ids = initialFormFields.map(f => f.id);
      expect(ids).toContain('fullName');
      expect(ids).toContain('birthDate');
      expect(ids).toContain('countryOfOrigin');
      expect(ids).toContain('existingLanguageCertificates');
      expect(ids).toContain('coursePreference');
      expect(ids).toContain('currentAddress');
      expect(ids).toContain('reasonForApplication');
    });

    it('coursePreference has correct options', () => {
      const courseField = initialFormFields.find(f => f.id === 'coursePreference');
      expect(courseField?.type).toBe('select');
      expect(courseField?.options).toEqual([
        'Intensive Course',
        'Evening Course',
        'Weekend Course'
      ]);
    });

    it('textarea fields are correctly typed', () => {
      const addressField = initialFormFields.find(f => f.id === 'currentAddress');
      const reasonField = initialFormFields.find(f => f.id === 'reasonForApplication');

      expect(addressField?.type).toBe('textarea');
      expect(reasonField?.type).toBe('textarea');
    });

    it('birthDate is date type', () => {
      const dateField = initialFormFields.find(f => f.id === 'birthDate');
      expect(dateField?.type).toBe('date');
    });
  });

  describe('sampleCaseFormData', () => {
    it('has entries for all mock cases', () => {
      expect(sampleCaseFormData['ACTE-2024-001']).toBeDefined();
      expect(sampleCaseFormData['ACTE-2024-002']).toBeDefined();
      expect(sampleCaseFormData['ACTE-2024-003']).toBeDefined();
    });

    it('each case has array structure', () => {
      Object.values(sampleCaseFormData).forEach(caseData => {
        expect(Array.isArray(caseData)).toBe(true);
        caseData.forEach(field => {
          expect(field).toHaveProperty('id');
          expect(field).toHaveProperty('label');
          expect(field).toHaveProperty('type');
          expect(field).toHaveProperty('value');
        });
      });
    });
  });

  describe('Form Field Validation', () => {
    it('all fields have valid structure', () => {
      initialFormFields.forEach(field => {
        expect(field).toHaveProperty('id');
        expect(field).toHaveProperty('label');
        expect(field).toHaveProperty('type');
        expect(field).toHaveProperty('value');
        expect(field).toHaveProperty('required');

        expect(typeof field.id).toBe('string');
        expect(typeof field.label).toBe('string');
        expect(['text', 'date', 'select', 'textarea']).toContain(field.type);
        expect(typeof field.value).toBe('string');
        expect(typeof field.required).toBe('boolean');

        if (field.type === 'select') {
          expect(field.options).toBeDefined();
          expect(Array.isArray(field.options)).toBe(true);
        }
      });
    });

    it('has unique field IDs', () => {
      const ids = initialFormFields.map(f => f.id);
      const uniqueIds = new Set(ids);
      expect(ids.length).toBe(uniqueIds.size);
    });

    it('initial values are empty strings', () => {
      initialFormFields.forEach(field => {
        expect(field.value).toBe('');
      });
    });
  });
});
