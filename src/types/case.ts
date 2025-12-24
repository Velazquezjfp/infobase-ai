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
}

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
