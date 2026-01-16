/**
 * Message Formatter Utility
 *
 * Provides utilities for formatting AI chat messages with:
 * - HTML sanitization (XSS prevention)
 * - Markdown rendering
 * - Code block detection
 * - Table data detection
 *
 * Part of S5-009: Improved Chat Information Presentation
 */

import React from 'react';
import DOMPurify from 'dompurify';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import CodeBlock from '@/components/ui/CodeBlock';
import DataTable from '@/components/workspace/DataTable';
import type { Components } from 'react-markdown';

/**
 * Sanitize HTML content to prevent XSS attacks.
 *
 * Removes dangerous elements and attributes while preserving safe HTML.
 * Used before rendering any user-generated or AI-generated content.
 *
 * @param content - Raw HTML content that may contain dangerous elements
 * @returns Sanitized HTML safe for rendering
 *
 * @example
 * sanitizeHTML('<script>alert("xss")</script><p>Safe text</p>')
 * // Returns: '<p>Safe text</p>'
 */
export function sanitizeHTML(content: string): string {
  return DOMPurify.sanitize(content, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 'code', 'pre',
      'ul', 'ol', 'li', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'span', 'div'
    ],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'class'],
    ALLOW_DATA_ATTR: false,
  });
}

/**
 * Render markdown content as React components.
 *
 * Converts markdown text to properly formatted React components with:
 * - Bold, italic, and other inline formatting
 * - Lists (bullet and numbered)
 * - Code blocks with syntax highlighting
 * - Tables
 * - Links that open in new tabs
 * - Headings
 *
 * @param content - Markdown formatted text
 * @returns React node with formatted content
 *
 * @example
 * renderMarkdown('**Bold** text with `code`')
 * // Returns: React components with <strong> and <code> elements
 */
export function renderMarkdown(content: string): React.ReactNode {
  // Custom components for markdown elements
  const components: Partial<Components> = {
    // Code blocks with syntax highlighting
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      const codeContent = String(children).replace(/\n$/, '');

      if (!inline && language) {
        return (
          <CodeBlock
            code={codeContent}
            language={language}
            showLineNumbers={false}
          />
        );
      }

      // Inline code
      return (
        <code
          className="px-1.5 py-0.5 text-sm bg-muted text-foreground rounded font-mono"
          {...props}
        >
          {children}
        </code>
      );
    },

    // Links that open in new tab
    a({ node, children, href, ...props }) {
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:underline"
          {...props}
        >
          {children}
        </a>
      );
    },

    // Tables with proper styling
    table({ node, children, ...props }) {
      return (
        <div className="my-4 overflow-x-auto">
          <table className="min-w-full border-collapse border border-border" {...props}>
            {children}
          </table>
        </div>
      );
    },

    thead({ node, children, ...props }) {
      return (
        <thead className="bg-muted" {...props}>
          {children}
        </thead>
      );
    },

    th({ node, children, ...props }) {
      return (
        <th className="border border-border px-4 py-2 text-left font-semibold" {...props}>
          {children}
        </th>
      );
    },

    td({ node, children, ...props }) {
      return (
        <td className="border border-border px-4 py-2" {...props}>
          {children}
        </td>
      );
    },

    // Paragraphs with spacing
    p({ node, children, ...props }) {
      return (
        <p className="mb-2 last:mb-0" {...props}>
          {children}
        </p>
      );
    },

    // Unordered lists
    ul({ node, children, ...props }) {
      return (
        <ul className="list-disc list-inside mb-2 space-y-1" {...props}>
          {children}
        </ul>
      );
    },

    // Ordered lists
    ol({ node, children, ...props }) {
      return (
        <ol className="list-decimal list-inside mb-2 space-y-1" {...props}>
          {children}
        </ol>
      );
    },

    // List items
    li({ node, children, ...props }) {
      return (
        <li className="ml-4" {...props}>
          {children}
        </li>
      );
    },

    // Headings
    h1({ node, children, ...props }) {
      return (
        <h1 className="text-2xl font-bold mb-2 mt-4" {...props}>
          {children}
        </h1>
      );
    },

    h2({ node, children, ...props }) {
      return (
        <h2 className="text-xl font-bold mb-2 mt-3" {...props}>
          {children}
        </h2>
      );
    },

    h3({ node, children, ...props }) {
      return (
        <h3 className="text-lg font-semibold mb-2 mt-2" {...props}>
          {children}
        </h3>
      );
    },

    // Blockquotes
    blockquote({ node, children, ...props }) {
      return (
        <blockquote className="border-l-4 border-primary pl-4 italic my-2" {...props}>
          {children}
        </blockquote>
      );
    },

    // Strong (bold)
    strong({ node, children, ...props }) {
      return (
        <strong className="font-bold" {...props}>
          {children}
        </strong>
      );
    },

    // Emphasis (italic)
    em({ node, children, ...props }) {
      return (
        <em className="italic" {...props}>
          {children}
        </em>
      );
    },
  };

  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={components}
    >
      {content}
    </ReactMarkdown>
  );
}

/**
 * Detect if content contains code blocks.
 *
 * Checks for markdown code block syntax (```).
 *
 * @param content - Text content to check
 * @returns True if code blocks are present
 */
export function detectCodeBlocks(content: string): boolean {
  return content.includes('```');
}

/**
 * Detect if content contains table data.
 *
 * Checks for markdown table syntax (|).
 *
 * @param content - Text content to check
 * @returns True if table markdown is present
 */
export function detectTableData(content: string): boolean {
  // Markdown tables have pipes and typically have header separator
  return content.includes('|') && content.includes('---');
}

/**
 * Preprocess content to preserve S2-004 source citation highlighting.
 *
 * Note: Slash command styling removed because:
 * 1. ReactMarkdown doesn't render raw HTML - spans appeared as literal text
 * 2. The regex /(\/\w+)/g was too greedy, matching normal text like "Einheiten/Woche"
 *
 * Slash commands are now styled at the component level in AIChatInterface.tsx
 *
 * @param content - Raw message content
 * @returns Content with preserved source citations
 */
function preprocessSourceCitations(content: string): string {
  // No preprocessing needed currently - emojis render correctly in markdown
  // and slash command styling has been moved to component level
  return content;
}

/**
 * Format a complete chat message with sanitization and markdown rendering.
 *
 * This is the main entry point for formatting AI responses.
 * Preserves S2-004 source citation highlighting while applying
 * S5-009 markdown rendering.
 *
 * @param content - Raw message content
 * @returns Formatted React node ready for rendering
 */
export function formatChatMessage(content: string): React.ReactNode {
  // First preprocess to preserve special styling (S2-004)
  const preprocessed = preprocessSourceCitations(content);

  // Then sanitize to remove any dangerous HTML (but allow our safe spans)
  const sanitized = sanitizeHTML(preprocessed);

  // Finally render markdown
  return renderMarkdown(sanitized);
}
