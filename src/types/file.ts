/**
 * TypeScript type definitions for file upload operations.
 *
 * These types support the drag-and-drop file upload feature (S4-001)
 * with proper type safety for upload results, progress tracking, and validation errors.
 */

/**
 * Result of a file upload operation.
 *
 * Returned by the backend /api/files/upload endpoint after successful upload.
 * Note: Backend uses snake_case (Python convention), so we use the same here.
 */
export interface UploadResult {
  /** Whether the upload was successful */
  success: boolean;

  /** Relative path to the uploaded file (e.g., "documents/ACTE-2024-001/uploads/file.pdf") */
  file_path: string;

  /** Name of the uploaded file */
  file_name: string;

  /** Size of the uploaded file in bytes */
  size: number;

  /** Optional success message from the server */
  message?: string;

  /** Optional error message if success is false */
  error?: string;
}

/**
 * Upload progress state for tracking file upload status.
 *
 * Used by FileDropZone and UploadProgress components to show real-time progress.
 */
export interface UploadProgress {
  /** Name of the file being uploaded */
  fileName: string;

  /** Upload progress percentage (0-100) */
  progress: number;

  /** Current status of the upload */
  status: 'idle' | 'uploading' | 'success' | 'error';

  /** Size of the file in bytes */
  size?: number;

  /** Error message if status is 'error' */
  error?: string;

  /** Timestamp when upload started */
  startedAt?: Date;

  /** Timestamp when upload completed */
  completedAt?: Date;
}

/**
 * File validation error types.
 *
 * Specific error codes for different validation failure scenarios.
 */
export type FileValidationErrorCode =
  | 'SIZE_EXCEEDED'      // File exceeds 15 MB limit
  | 'INVALID_TYPE'       // File type not allowed
  | 'INVALID_NAME'       // Invalid filename
  | 'NETWORK_ERROR'      // Network failure during upload
  | 'SERVER_ERROR'       // Server-side error
  | 'UNKNOWN_ERROR';     // Unknown error

/**
 * File validation error details.
 *
 * Provides structured error information for better error handling and user feedback.
 */
export interface FileValidationError {
  /** Error code identifying the type of error */
  code: FileValidationErrorCode;

  /** Human-readable error message */
  message: string;

  /** Name of the file that failed validation */
  fileName: string;

  /** Optional additional details about the error */
  detail?: string;
}

/**
 * Configuration for file upload constraints.
 *
 * Defines limits and rules for file uploads.
 */
export interface UploadConstraints {
  /** Maximum file size in bytes (default: 15 MB) */
  maxSizeBytes: number;

  /** Maximum file size in megabytes (for display) */
  maxSizeMB: number;

  /** Allowed file extensions (if undefined, all types allowed) */
  allowedExtensions?: string[];

  /** Target folder ID (default: "uploads") */
  defaultFolderId: string;
}

/**
 * Default upload constraints for S4-001.
 */
export const DEFAULT_UPLOAD_CONSTRAINTS: UploadConstraints = {
  maxSizeBytes: 15 * 1024 * 1024, // 15 MB
  maxSizeMB: 15,
  defaultFolderId: 'uploads',
  // allowedExtensions: undefined means all file types are allowed
};

/**
 * File upload request parameters.
 *
 * Parameters needed to upload a file to the backend.
 */
export interface UploadRequest {
  /** The file to upload */
  file: File;

  /** Case ID where the file should be stored */
  caseId: string;

  /** Folder ID within the case (default: "uploads") */
  folderId?: string;

  /** Optional callback for progress updates */
  onProgress?: (progress: number) => void;

  /** Optional alternative filename (for duplicate handling) */
  renameTo?: string;
}

/**
 * Multiple file upload state.
 *
 * Tracks state for multiple concurrent file uploads.
 */
export interface MultiUploadState {
  /** Map of file names to their upload progress */
  files: Map<string, UploadProgress>;

  /** Total number of files to upload */
  totalFiles: number;

  /** Number of successfully uploaded files */
  successCount: number;

  /** Number of failed uploads */
  errorCount: number;

  /** Whether all uploads are complete */
  isComplete: boolean;
}
