/**
 * Type definitions for Case Context and Document Tree View
 *
 * S5-011: Cascading Context with Document Tree View
 * These types define the structure for the document tree view that provides
 * AI agents with global awareness of all documents in a case.
 */

/**
 * Node in the document tree structure
 * Can represent either a folder or a document
 */
export interface TreeNode {
  name: string;
  type: 'folder' | 'document';
  children?: TreeNode[];
  id?: string;
  isEmpty?: boolean;
}

/**
 * Document Tree View structure
 *
 * Contains a hierarchical text representation of all folders and documents
 * in a case, used for AI context awareness.
 */
export interface DocumentTreeView {
  caseId: string;
  treeStructure: string;  // Hierarchical text format with ├── └── characters
  lastUpdated: string;     // ISO 8601 timestamp
  documentCount?: number;
  folders?: string[];
}

/**
 * API response for tree view endpoint
 */
export interface TreeViewResponse {
  treeView: string;
  folders: string[];
  documentCount: number;
}
