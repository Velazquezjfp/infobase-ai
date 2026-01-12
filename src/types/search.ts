/**
 * S5-003: Search Types for Semantic Search Feature
 *
 * Type definitions for semantic search functionality including
 * search highlights, text blocks, and API request/response types.
 */

/**
 * Represents a highlighted text segment in search results.
 */
export interface SearchHighlight {
  /** Starting character position in the document text */
  start: number;

  /** Ending character position in the document text */
  end: number;

  /** Relevance score from 0.0 to 1.0 indicating match quality */
  relevance: number;

  /** The actual text that matched the search query */
  matchedText: string;

  /** Brief explanation of why this text matches the query */
  context: string;
}

/**
 * Represents a text block from a PDF with position information.
 * Used for PDF text extraction and positioning.
 */
export interface TextBlock {
  /** The text content of this block */
  text: string;

  /** Page number (1-indexed) */
  page: number;

  /** Position coordinates on the page */
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };

  /** Starting character index in the full document */
  charStart?: number;

  /** Ending character index in the full document */
  charEnd?: number;
}

/**
 * Request payload for semantic search API.
 */
export interface SemanticSearchRequest {
  /** The search query in natural language */
  query: string;

  /** The full text content of the document to search */
  documentContent: string;

  /** Type of the document (pdf, txt, etc.) */
  documentType: string;

  /** Language of the search query (ISO 639-1 code: en, de, etc.) */
  queryLanguage?: string;

  /** Language of the document (ISO 639-1 code: en, de, etc.) */
  documentLanguage?: string;
}

/**
 * Response from semantic search API.
 */
export interface SemanticSearchResponse {
  /** Array of highlighted text segments matching the query */
  highlights: SearchHighlight[];

  /** Total number of matches found */
  count: number;

  /** Brief summary of what was found */
  matchSummary: string;
}

/**
 * Search state maintained in the application context.
 */
export interface SearchState {
  /** Current search query */
  query: string;

  /** Array of highlights in the current document */
  highlights: SearchHighlight[];

  /** Index of the currently active/focused highlight */
  activeIndex: number;

  /** Whether a search is in progress */
  isSearching: boolean;
}
