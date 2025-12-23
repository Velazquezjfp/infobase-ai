/**
 * Admin API Client for BAMF AI Case Management System
 *
 * This module provides type-safe client functions for the admin REST API,
 * including AI-powered form field generation.
 */

import type { FormField } from '../types/case';
import type { SHACLPropertyShape } from '../types/shacl';

/**
 * API configuration
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Request payload for generating a form field
 */
export interface GenerateFieldRequest {
  /** Natural language prompt describing the field to generate */
  prompt: string;
}

/**
 * Response from the field generation endpoint
 */
export interface GenerateFieldResponse {
  field: FormField;
  message: string;
}

/**
 * API error response structure
 */
export interface ApiError {
  error: string;
  detail?: string;
  validation_errors?: string[];
}

/**
 * Custom error class for API errors
 */
export class AdminApiError extends Error {
  public readonly statusCode: number;
  public readonly detail?: string;
  public readonly validationErrors?: string[];

  constructor(
    message: string,
    statusCode: number,
    detail?: string,
    validationErrors?: string[]
  ) {
    super(message);
    this.name = 'AdminApiError';
    this.statusCode = statusCode;
    this.detail = detail;
    this.validationErrors = validationErrors;
  }
}

/**
 * Generate a form field from a natural language prompt.
 *
 * Uses AI (Gemini) to interpret the prompt and generate a SHACL-compliant
 * form field specification.
 *
 * @param prompt - Natural language description of the desired field
 * @returns Promise resolving to the generated FormField with SHACL metadata
 * @throws AdminApiError if the request fails
 *
 * @example
 * ```typescript
 * try {
 *   const field = await generateField(
 *     "Add a dropdown for marital status with options single, married, divorced"
 *   );
 *   console.log(field.label); // "Marital Status"
 *   console.log(field.type);  // "select"
 *   console.log(field.options); // ["Single", "Married", "Divorced"]
 * } catch (error) {
 *   if (error instanceof AdminApiError) {
 *     console.error(`API Error (${error.statusCode}): ${error.message}`);
 *   }
 * }
 * ```
 */
export async function generateField(prompt: string): Promise<FormField> {
  const url = `${API_BASE_URL}/api/admin/generate-field`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({})) as ApiError;
      throw new AdminApiError(
        errorData.error || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        typeof errorData.detail === 'string' ? errorData.detail : undefined,
        errorData.validation_errors
      );
    }

    const data = (await response.json()) as GenerateFieldResponse;
    return data.field;
  } catch (error) {
    // Re-throw AdminApiError as-is
    if (error instanceof AdminApiError) {
      throw error;
    }

    // Handle network errors
    if (error instanceof TypeError) {
      throw new AdminApiError(
        'Network error: Unable to connect to the server',
        0,
        'Please check if the backend server is running'
      );
    }

    // Handle other errors
    throw new AdminApiError(
      error instanceof Error ? error.message : 'Unknown error occurred',
      500
    );
  }
}

/**
 * Check the health status of the admin API.
 *
 * @returns Promise resolving to health status
 * @throws AdminApiError if the health check fails
 */
export async function checkAdminHealth(): Promise<{
  service: string;
  status: string;
  features: Record<string, boolean>;
}> {
  const url = `${API_BASE_URL}/api/admin/health`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new AdminApiError(
        'Admin service health check failed',
        response.status
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof AdminApiError) {
      throw error;
    }

    throw new AdminApiError(
      'Failed to check admin service health',
      0,
      error instanceof Error ? error.message : undefined
    );
  }
}

/**
 * Validate a field generation prompt before sending to the API.
 *
 * @param prompt - The prompt to validate
 * @returns Object with isValid boolean and optional error message
 */
export function validatePrompt(prompt: string): {
  isValid: boolean;
  error?: string;
} {
  const trimmedPrompt = prompt.trim();

  if (!trimmedPrompt) {
    return { isValid: false, error: 'Prompt cannot be empty' };
  }

  if (trimmedPrompt.length < 3) {
    return { isValid: false, error: 'Prompt must be at least 3 characters' };
  }

  if (trimmedPrompt.length > 500) {
    return { isValid: false, error: 'Prompt must be less than 500 characters' };
  }

  return { isValid: true };
}

/**
 * Helper function to extract field type hint from a prompt.
 * Useful for showing preview/suggestions in the UI.
 *
 * @param prompt - The user's prompt
 * @returns Suggested field type or null if unclear
 */
export function suggestFieldType(
  prompt: string
): 'text' | 'date' | 'select' | 'textarea' | null {
  const lower = prompt.toLowerCase();

  if (
    lower.includes('dropdown') ||
    lower.includes('select') ||
    lower.includes('choice') ||
    lower.includes('options')
  ) {
    return 'select';
  }

  if (
    lower.includes('date') ||
    lower.includes('birthday') ||
    lower.includes('expiry') ||
    lower.includes('datum')
  ) {
    return 'date';
  }

  if (
    lower.includes('textarea') ||
    lower.includes('long text') ||
    lower.includes('description') ||
    lower.includes('notes') ||
    lower.includes('paragraph')
  ) {
    return 'textarea';
  }

  // Default to text for any field request
  if (
    lower.includes('field') ||
    lower.includes('input') ||
    lower.includes('add') ||
    lower.includes('create')
  ) {
    return 'text';
  }

  return null;
}
