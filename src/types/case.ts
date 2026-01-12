import type { SHACLPropertyShape } from './shacl';

export interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'xml' | 'json' | 'docx' | 'txt' | 'jpg' | 'jpeg' | 'png' | 'gif' | 'webp' | 'bmp';
  size: string;
  uploadedAt: string;
  metadata: Record<string, string>;
  content?: string;
  caseId?: string;    // For case-scoped path construction
  folderId?: string;  // For case-scoped path construction
}

export interface Folder {
  id: string;
  name: string;
  documents: Document[];
  subfolders: Folder[];
  isExpanded?: boolean;
}

export interface Case {
  id: string;
  name: string;
  createdAt: string;
  status: 'open' | 'pending' | 'completed';
  folders: Folder[];
}

export interface FormField {
  id: string;
  label: string;
  type: 'text' | 'date' | 'select' | 'textarea';
  value: string;
  options?: string[];
  required?: boolean;
  /** SHACL metadata for semantic form field definition (Sprint 2) */
  shaclMetadata?: SHACLPropertyShape;
  /** S5-001: Validation pattern (regex) for client-side validation */
  validationPattern?: string;
  /** S5-001: Schema.org semantic type (e.g., "schema:email", "schema:name") */
  semanticType?: string;
}

/**
 * S5-002: Suggested value for a form field
 * Used when AI extracts a value different from the current field value
 */
export interface SuggestedValue {
  fieldId: string;
  value: string;
  confidence: number;
  current: string;
}

/**
 * S5-002: Map of field IDs to their suggested values
 */
export type FormSuggestions = Record<string, SuggestedValue>;

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  command?: string;
}

export interface SlashCommand {
  command: string;
  label: string;
  description: string;
  icon: string;
}
