import type { SHACLPropertyShape } from './shacl';

/**
 * S5-006: Render type for document versions
 */
export type RenderType = 'original' | 'anonymized' | 'translated' | 'annotated';

/**
 * S5-006: Document render metadata
 * Represents a specific version/render of a document
 */
export interface DocumentRender {
  id: string;
  type: RenderType;
  name: string;
  filePath: string;
  createdAt: string;
  metadata?: Record<string, any>;
}

export interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'xml' | 'json' | 'docx' | 'txt' | 'jpg' | 'jpeg' | 'png' | 'gif' | 'webp' | 'bmp' | 'eml';
  size: string;
  uploadedAt: string;
  metadata: Record<string, string>;
  content?: string;
  caseId?: string;    // For case-scoped path construction
  folderId?: string;  // For case-scoped path construction
  /** S5-006: Array of document renders (original, anonymized, translated, etc.) */
  renders?: DocumentRender[];
}

export interface LocalizedFolderName {
  de: string;
  en: string;
}

export interface Folder {
  id: string;
  name: string;
  nameKey?: string;
  localizedName?: LocalizedFolderName;
  documents: Document[];
  subfolders: Folder[];
  isExpanded?: boolean;
  mandatory?: boolean;
  order?: number;
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

/**
 * Custom Context Rule Types for /Aktenkontext commands
 * S5-017: Context modification via slash commands
 */
export type CustomRuleType = 'validation_rule' | 'required_document';

export interface CustomContextRule {
  id: string;
  type: CustomRuleType;
  createdAt: string;
  targetFolder?: string;  // For folder-specific rules
  rule: string;           // The rule text
  ruleType?: string;      // Sub-type (e.g., 'file_type', 'content', 'metadata')
}

/**
 * Hierarchical slash command argument
 * Supports nested command completion like /Aktenkontext Regeln Ordner
 */
export interface SlashCommandArgument {
  value: string;
  label: string;
  description: string;
  children?: SlashCommandArgument[];
  requiresInput?: boolean;  // If true, expects free-form text input after
  placeholder?: string;     // Placeholder text for free-form input
}

/**
 * Extended slash command with hierarchical arguments
 */
export interface HierarchicalSlashCommand extends SlashCommand {
  arguments?: SlashCommandArgument[];
  isDynamic?: boolean;      // If true, arguments come from context (e.g., existing rules)
  dynamicSource?: string;   // Source for dynamic arguments (e.g., 'customRules')
}
