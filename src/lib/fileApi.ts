/**
 * File API Client for BAMF AI Case Management System.
 *
 * This module provides API client functions for file operations including
 * upload with progress tracking, validation, and error handling.
 */

import type {
  UploadResult,
  UploadRequest,
  FileValidationError,
  DEFAULT_UPLOAD_CONSTRAINTS,
} from '@/types/file';

// Backend API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Validate file size before upload.
 *
 * Provides immediate client-side feedback without making a request to the server.
 *
 * @param file - The file to validate
 * @param maxSizeMB - Maximum allowed size in megabytes (default: 15 MB)
 * @returns FileValidationError if validation fails, null otherwise
 */
export function validateFileSize(
  file: File,
  maxSizeMB: number = 15
): FileValidationError | null {
  const maxSizeBytes = maxSizeMB * 1024 * 1024;

  if (file.size > maxSizeBytes) {
    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
    return {
      code: 'SIZE_EXCEEDED',
      message: `File exceeds ${maxSizeMB} MB limit`,
      fileName: file.name,
      detail: `File size: ${fileSizeMB} MB. Maximum: ${maxSizeMB} MB`,
    };
  }

  if (file.size === 0) {
    return {
      code: 'INVALID_NAME',
      message: 'File is empty (0 bytes)',
      fileName: file.name,
    };
  }

  return null;
}

/**
 * Validate file extension.
 *
 * @param file - The file to validate
 * @param allowedExtensions - List of allowed extensions (e.g., ['.pdf', '.jpg'])
 * @returns FileValidationError if validation fails, null otherwise
 */
export function validateFileExtension(
  file: File,
  allowedExtensions?: string[]
): FileValidationError | null {
  if (!allowedExtensions || allowedExtensions.length === 0) {
    return null; // All extensions allowed
  }

  const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();

  if (!allowedExtensions.some(ext => ext.toLowerCase() === fileExt)) {
    return {
      code: 'INVALID_TYPE',
      message: `File type not allowed: ${fileExt}`,
      fileName: file.name,
      detail: `Allowed types: ${allowedExtensions.join(', ')}`,
    };
  }

  return null;
}

/**
 * Upload a file to the backend server.
 *
 * Uses FormData and fetch API for multipart/form-data upload.
 * Includes progress tracking via XMLHttpRequest if onProgress callback is provided.
 *
 * @param request - Upload request parameters
 * @returns Promise resolving to UploadResult
 * @throws Error if upload fails
 *
 * @example
 * ```typescript
 * const result = await uploadFile({
 *   file: selectedFile,
 *   caseId: 'ACTE-2024-001',
 *   folderId: 'uploads',
 *   onProgress: (progress) => console.log(`${progress}% complete`)
 * });
 * ```
 */
export async function uploadFile(request: UploadRequest): Promise<UploadResult> {
  const { file, caseId, folderId = 'uploads', onProgress, renameTo } = request;

  // Client-side validation
  const sizeError = validateFileSize(file);
  if (sizeError) {
    throw new Error(sizeError.message);
  }

  // Create FormData
  const formData = new FormData();
  formData.append('file', file);
  formData.append('case_id', caseId);
  formData.append('folder_id', folderId);

  // Add rename_to parameter if provided (for duplicate handling)
  if (renameTo) {
    formData.append('rename_to', renameTo);
  }

  // Use XMLHttpRequest if progress tracking is needed
  if (onProgress) {
    return uploadFileWithProgress(formData, onProgress);
  }

  // Otherwise use fetch API (simpler but no progress tracking)
  return uploadFileSimple(formData);
}

/**
 * Upload file using fetch API (no progress tracking).
 *
 * @param formData - FormData containing file and parameters
 * @returns Promise resolving to UploadResult
 */
async function uploadFileSimple(formData: FormData): Promise<UploadResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/files/upload`, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header - browser will set it with boundary for multipart/form-data
    });

    const result = await response.json();

    if (!response.ok) {
      // Server returned an error
      const errorMessage = result.detail?.error || result.error || 'Upload failed';
      const errorDetail = result.detail?.detail || result.detail || '';

      throw new Error(errorDetail ? `${errorMessage}: ${errorDetail}` : errorMessage);
    }

    return result as UploadResult;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Network error during file upload');
  }
}

/**
 * Upload file using XMLHttpRequest with progress tracking.
 *
 * @param formData - FormData containing file and parameters
 * @param onProgress - Callback for progress updates (0-100)
 * @returns Promise resolving to UploadResult
 */
async function uploadFileWithProgress(
  formData: FormData,
  onProgress: (progress: number) => void
): Promise<UploadResult> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // Progress event listener
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percentComplete = Math.round((event.loaded / event.total) * 100);
        onProgress(percentComplete);
      }
    });

    // Load event listener (success)
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const result = JSON.parse(xhr.responseText) as UploadResult;
          onProgress(100); // Ensure progress reaches 100%
          resolve(result);
        } catch (error) {
          reject(new Error('Failed to parse server response'));
        }
      } else {
        try {
          const errorResult = JSON.parse(xhr.responseText);
          const errorMessage = errorResult.detail?.error || errorResult.error || 'Upload failed';
          const errorDetail = errorResult.detail?.detail || errorResult.detail || '';
          reject(new Error(errorDetail ? `${errorMessage}: ${errorDetail}` : errorMessage));
        } catch {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      }
    });

    // Error event listener
    xhr.addEventListener('error', () => {
      reject(new Error('Network error during file upload'));
    });

    // Abort event listener
    xhr.addEventListener('abort', () => {
      reject(new Error('Upload cancelled'));
    });

    // Timeout event listener
    xhr.addEventListener('timeout', () => {
      reject(new Error('Upload timeout'));
    });

    // Open and send request
    xhr.open('POST', `${API_BASE_URL}/api/files/upload`);
    xhr.timeout = 120000; // 2 minute timeout for large files
    xhr.send(formData);
  });
}

/**
 * Check if the file service is available.
 *
 * @returns Promise resolving to true if service is healthy, false otherwise
 */
export async function checkFileServiceHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/files/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      return false;
    }

    const result = await response.json();
    return result.status === 'ready';
  } catch (error) {
    console.error('File service health check failed:', error);
    return false;
  }
}

/**
 * Format file size for display.
 *
 * @param bytes - File size in bytes
 * @returns Formatted string (e.g., "5.2 MB", "128 KB")
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Get file extension from filename.
 *
 * @param filename - Name of the file
 * @returns File extension including the dot (e.g., ".pdf"), or empty string if no extension
 */
export function getFileExtension(filename: string): string {
  const parts = filename.split('.');
  return parts.length > 1 ? `.${parts.pop()?.toLowerCase()}` : '';
}

/**
 * Result of a file deletion operation.
 */
export interface DeleteResult {
  /** Whether the deletion was successful */
  success: boolean;
  /** Success or error message */
  message: string;
  /** Name of the deleted file */
  file_name: string;
}

/**
 * Result of a file existence check.
 */
export interface FileExistsResult {
  /** Whether the file exists */
  exists: boolean;
  /** The sanitized filename that was checked */
  file_name: string;
  /** Suggested unique filename if file exists (e.g., "document_1.pdf") */
  suggested_name?: string;
}

/**
 * Delete a file from a case folder.
 *
 * Calls the backend DELETE endpoint with security validation.
 *
 * @param caseId - The case ID (e.g., "ACTE-2024-001")
 * @param folderId - The folder ID (e.g., "uploads")
 * @param filename - The name of the file to delete
 * @returns Promise resolving to DeleteResult
 * @throws Error if deletion fails
 *
 * @example
 * ```typescript
 * try {
 *   const result = await deleteFile('ACTE-2024-001', 'uploads', 'document.pdf');
 *   console.log(result.message); // "File 'document.pdf' deleted successfully"
 * } catch (error) {
 *   console.error('Deletion failed:', error.message);
 * }
 * ```
 */
export async function deleteFile(
  caseId: string,
  folderId: string,
  filename: string
): Promise<DeleteResult> {
  try {
    // Encode URI components to handle special characters in filename
    const encodedCaseId = encodeURIComponent(caseId);
    const encodedFolderId = encodeURIComponent(folderId);
    const encodedFilename = encodeURIComponent(filename);

    const response = await fetch(
      `${API_BASE_URL}/api/files/${encodedCaseId}/${encodedFolderId}/${encodedFilename}`,
      {
        method: 'DELETE',
      }
    );

    const result = await response.json();

    if (!response.ok) {
      // Server returned an error
      const errorMessage = result.detail?.error || result.error || 'Deletion failed';
      const errorDetail = result.detail?.detail || result.detail || '';

      throw new Error(errorDetail ? `${errorMessage}: ${errorDetail}` : errorMessage);
    }

    return result as DeleteResult;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Network error during file deletion');
  }
}

/**
 * Check if a file already exists in a case folder.
 *
 * Use this before uploading to detect duplicates and give users
 * the option to rename or cancel.
 *
 * @param caseId - The case ID (e.g., "ACTE-2024-001")
 * @param folderId - The folder ID (e.g., "uploads")
 * @param filename - The name of the file to check
 * @returns Promise resolving to FileExistsResult
 * @throws Error if the check fails
 *
 * @example
 * ```typescript
 * const result = await checkFileExists('ACTE-2024-001', 'uploads', 'document.pdf');
 * if (result.exists) {
 *   console.log(`File exists. Suggested name: ${result.suggested_name}`);
 * }
 * ```
 */
export async function checkFileExists(
  caseId: string,
  folderId: string,
  filename: string
): Promise<FileExistsResult> {
  try {
    // Encode URI components to handle special characters in filename
    const encodedCaseId = encodeURIComponent(caseId);
    const encodedFolderId = encodeURIComponent(folderId);
    const encodedFilename = encodeURIComponent(filename);

    const response = await fetch(
      `${API_BASE_URL}/api/files/exists/${encodedCaseId}/${encodedFolderId}/${encodedFilename}`,
      {
        method: 'GET',
      }
    );

    const result = await response.json();

    if (!response.ok) {
      const errorMessage = result.detail?.error || result.error || 'Check failed';
      const errorDetail = result.detail?.detail || result.detail || '';

      throw new Error(errorDetail ? `${errorMessage}: ${errorDetail}` : errorMessage);
    }

    return result as FileExistsResult;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Network error during file existence check');
  }
}
