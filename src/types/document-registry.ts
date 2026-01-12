/**
 * Document Registry Type Definitions
 *
 * Type definitions for the BAMF ACTE Companion document registry system.
 * These types correspond to the JSON Schema defined in:
 * backend/schemas/document_registry_schema.json
 *
 * The document registry tracks all documents, their metadata, renders
 * (anonymized and translated versions), and folder locations. The registry
 * persists across application restarts and provides the source of truth
 * for the document tree structure.
 *
 * @see D-S5-002 - Document Registry Schema
 */

/**
 * Represents a render (anonymized or translated version) of a document.
 *
 * Renders are alternative versions of documents that have been processed:
 * - Anonymized: PII (Personally Identifiable Information) removed/redacted
 * - Translated: Converted to a different language
 */
export interface DocumentRender {
  /**
   * Unique identifier for this render.
   * Format: String ID (e.g., "render_001")
   */
  renderId: string;

  /**
   * Type of render.
   * - "anonymized": Document with PII removed/redacted
   * - "translated": Document translated to another language
   */
  type: 'anonymized' | 'translated';

  /**
   * File path to the rendered document.
   * Relative path from application root.
   * Example: "public/documents/ACTE-2024-001/personal-data/Birth_Certificate_anonymized.jpg"
   */
  filePath: string;

  /**
   * Timestamp when render was created.
   * Format: ISO 8601 (e.g., "2026-01-08T10:15:00Z")
   */
  createdAt: string;

  /**
   * Language code for translated renders.
   * Format: ISO 639-1 two-letter code (e.g., "en", "de", "fr")
   * Required when type is "translated", optional for "anonymized"
   */
  language?: string;
}

/**
 * Represents a document entry in the registry.
 *
 * Each document entry contains the original document metadata plus
 * an array of renders (alternative processed versions).
 */
export interface DocumentRegistryEntry {
  /**
   * Unique identifier for the document.
   * Format: String ID (e.g., "doc_001")
   */
  documentId: string;

  /**
   * Case ID this document belongs to.
   * Example: "ACTE-2024-001"
   */
  caseId: string;

  /**
   * Optional folder ID within the case.
   * Example: "personal-data", "certificates", "emails"
   * If omitted, document exists at case root level.
   */
  folderId?: string;

  /**
   * Original filename of the document.
   * Example: "Birth_Certificate.jpg"
   */
  fileName: string;

  /**
   * File path to the original document.
   * Relative path from application root.
   * Example: "public/documents/ACTE-2024-001/personal-data/Birth_Certificate.jpg"
   */
  filePath: string;

  /**
   * Timestamp when document was uploaded.
   * Format: ISO 8601 (e.g., "2026-01-08T10:00:00Z")
   */
  uploadedAt: string;

  /**
   * File integrity hash for detecting file corruption or tampering.
   * Format: "sha256:" prefix followed by 64 hexadecimal characters
   * Example: "sha256:1234567890abcdef..."
   */
  fileHash: string;

  /**
   * Array of rendered versions of this document.
   * Can be empty if no renders have been created yet.
   * Includes anonymized versions, translations, etc.
   */
  renders: DocumentRender[];
}

/**
 * Root structure of the document registry manifest.
 *
 * The manifest is persisted as a JSON file and loaded on application startup.
 * It serves as the single source of truth for all document metadata.
 */
export interface DocumentRegistry {
  /**
   * Registry format version.
   * Format: "major.minor" (e.g., "1.0")
   * Used for migration logic if registry format changes.
   */
  version: string;

  /**
   * JSON Schema version used for validation.
   * Format: "major.minor" (e.g., "1.0")
   * References the schema version in backend/schemas/document_registry_schema.json
   */
  schemaVersion: string;

  /**
   * Timestamp of last update to the registry.
   * Format: ISO 8601 (e.g., "2026-01-09T16:00:00Z")
   * Updated whenever documents are added, removed, or renders are created.
   */
  lastUpdated: string;

  /**
   * Array of all registered documents.
   * Empty array if no documents have been registered yet.
   */
  documents: DocumentRegistryEntry[];
}

/**
 * Type guard to check if a render is a translated render with language field.
 */
export function isTranslatedRender(render: DocumentRender): render is DocumentRender & { language: string } {
  return render.type === 'translated' && typeof render.language === 'string';
}

/**
 * Type guard to check if a render is an anonymized render.
 */
export function isAnonymizedRender(render: DocumentRender): boolean {
  return render.type === 'anonymized';
}
