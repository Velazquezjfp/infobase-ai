/**
 * WebSocket Message Types for BAMF AI Case Management System
 *
 * Defines TypeScript interfaces for WebSocket communication between
 * the frontend and backend AI services.
 */

import { FormField } from './case';

/**
 * Base message interface with common fields
 */
export interface BaseMessage {
  type: string;
  timestamp?: string;
}

/**
 * Chat request message sent from client to server
 */
export interface ChatRequest extends BaseMessage {
  type: 'chat';
  content: string;
  caseId: string;
  folderId?: string | null;
  documentContent?: string;
  formSchema?: FormField[];
  stream?: boolean;
}

/**
 * Chat response message sent from server to client
 */
export interface ChatResponse extends BaseMessage {
  type: 'chat_response';
  content: string;
  timestamp: string;
}

/**
 * Chat chunk message for streaming responses
 */
export interface ChatChunkMessage extends BaseMessage {
  type: 'chat_chunk';
  content: string;
  is_complete: boolean;
  timestamp?: string;
}

/**
 * Form update message sent from server after field extraction
 */
export interface FormUpdateMessage extends BaseMessage {
  type: 'form_update';
  updates: Record<string, string>;
  confidence: Record<string, number>;
  timestamp?: string;
}

/**
 * S5-002: Form suggestion message sent from server for non-empty fields
 * Displays inline suggestions with accept/reject actions
 */
export interface FormSuggestionMessage extends BaseMessage {
  type: 'form_suggestion';
  suggestions: Record<string, {
    value: string;
    confidence: number;
    current: string;
  }>;
  timestamp?: string;
}

/**
 * System message for connection status and notifications
 */
export interface SystemMessage extends BaseMessage {
  type: 'system';
  content: string;
  timestamp?: string;
}

/**
 * Error message sent when something goes wrong
 */
export interface ErrorMessage extends BaseMessage {
  type: 'error';
  message: string;
  timestamp?: string;
}

/**
 * Anonymization request message sent from client to server
 */
export interface AnonymizationRequest extends BaseMessage {
  type: 'anonymize';
  filePath: string;
  caseId: string;
  folderId?: string;
  documentId?: string; // S5-006: Document ID for render registration
  language?: string;   // S5-014: Language for response messages (de/en)
}

/**
 * Detection info for a single anonymized field
 */
export interface DetectionInfo {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
}

/**
 * Anonymization response message sent from server after anonymization completes
 */
export interface AnonymizationResponse extends BaseMessage {
  type: 'anonymization_complete';
  originalPath: string;
  anonymizedPath: string | null;
  detectionsCount: number;
  detectionLabels?: string[];  // List of field names that were anonymized
  detections?: Record<string, DetectionInfo[]>;  // Full detection data with coordinates
  success: boolean;
  error?: string;
  timestamp?: string;
  renderMetadata?: any; // S5-006: Render metadata from document registry
  documentId?: string;   // S5-006: Document ID that was anonymized
}

/**
 * S5-004/S5-008: Translation request message sent from client to server
 */
export interface TranslationRequest extends BaseMessage {
  type: 'translate';
  filePath: string;
  caseId: string;
  folderId?: string;
  documentId?: string;
  targetLanguage?: string; // ISO 639-1 code (de, en, ar, etc.), default: de
  sourceLanguage?: string; // ISO 639-1 code or 'auto', default: auto
}

/**
 * S5-004/S5-008: Translation response message sent from server after translation completes
 */
export interface TranslationResponse extends BaseMessage {
  type: 'translation_complete';
  originalPath: string;
  translatedPath: string | null;
  sourceLanguage?: string;
  targetLanguage?: string;
  success: boolean;
  error?: string;
  timestamp?: string;
  renderMetadata?: any; // S5-006: Render metadata from document registry
  documentId?: string;   // S5-006: Document ID that was translated
}

/**
 * Union type of all possible WebSocket messages from server
 */
export type WebSocketMessage =
  | ChatResponse
  | ChatChunkMessage
  | FormUpdateMessage
  | FormSuggestionMessage
  | SystemMessage
  | ErrorMessage
  | AnonymizationResponse
  | TranslationResponse;

/**
 * WebSocket connection status
 */
export type ConnectionStatus =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'error';

/**
 * WebSocket connection state interface
 */
export interface WebSocketState {
  connection: WebSocket | null;
  status: ConnectionStatus;
  error: string | null;
}
