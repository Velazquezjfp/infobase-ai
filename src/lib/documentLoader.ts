/**
 * Document Loader Utility for Case-Instance Scoped Document Loading
 *
 * This utility provides case-aware document loading functionality that ensures
 * complete isolation between cases (ACTEs). Documents are loaded from
 * case-specific directories: /documents/{caseId}/{folderId}/{filename}
 */

/**
 * Loads document content from case-specific directory path.
 *
 * @param caseId - The case identifier (e.g., "ACTE-2024-001")
 * @param folderId - The folder identifier (e.g., "personal-data")
 * @param filename - The document filename (e.g., "Birth_Certificate.txt")
 * @returns Promise resolving to the document content as a string
 * @throws Error if document cannot be loaded (404, network error, etc.)
 *
 * @example
 * ```typescript
 * const content = await loadDocumentContent(
 *   'ACTE-2024-001',
 *   'personal-data',
 *   'Birth_Certificate.txt'
 * );
 * ```
 */
export async function loadDocumentContent(
  caseId: string,
  folderId: string,
  filename: string,
  signal?: AbortSignal
): Promise<string> {
  // Construct case-scoped path
  const path = `/documents/${caseId}/${folderId}/${filename}`;

  try {
    const response = await fetch(path, {
      method: 'GET',
      signal, // Support for request cancellation
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`Document not found: ${path}`);
      }
      throw new Error(`Failed to load document: ${response.statusText} (${response.status})`);
    }

    // Read as text to preserve UTF-8 encoding
    const content = await response.text();

    return content;
  } catch (error) {
    // Handle AbortError separately (not a real error)
    if (error instanceof Error && error.name === 'AbortError') {
      throw error; // Re-throw to let caller handle
    }

    // Handle network errors
    if (error instanceof TypeError) {
      throw new Error(`Network error loading document: ${path}`);
    }

    // Re-throw other errors
    throw error;
  }
}

/**
 * Creates an AbortController for cancellable document loading.
 * Useful for preventing race conditions when rapidly switching documents.
 *
 * @returns AbortController instance
 *
 * @example
 * ```typescript
 * const controller = createLoadController();
 * try {
 *   const content = await loadDocumentContent(
 *     caseId,
 *     folderId,
 *     filename,
 *     controller.signal
 *   );
 * } catch (error) {
 *   if (error.name === 'AbortError') {
 *     // Request was cancelled
 *   }
 * }
 * // Cancel if needed: controller.abort();
 * ```
 */
export function createLoadController(): AbortController {
  return new AbortController();
}

/**
 * Validates if a document path is accessible within the given case scope.
 * Used for security checks to prevent cross-case document access.
 *
 * @param requestedCaseId - The case ID being requested
 * @param activeCaseId - The currently active case ID
 * @returns true if access is allowed, false otherwise
 */
export function validateCaseAccess(
  requestedCaseId: string,
  activeCaseId: string
): boolean {
  // Only allow access to documents from the active case
  return requestedCaseId === activeCaseId;
}
