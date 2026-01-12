/**
 * S5-003: HighlightedText Component
 *
 * Component for rendering text with search highlights.
 * Splits text into segments and wraps highlighted portions in <mark> elements.
 *
 * Features:
 * - Multiple highlights support
 * - Active highlight indicator
 * - Visual distinction between active and inactive highlights
 * - Smooth transitions
 */

import React, { useRef, useEffect } from 'react';
import { SearchHighlight } from '@/types/search';

interface HighlightedTextProps {
  /** The full text content to render */
  text: string;

  /** Array of highlights to apply */
  highlights: SearchHighlight[];

  /** Index of the currently active (focused) highlight */
  activeHighlightIndex: number;

  /** Callback to set highlight refs for scrolling */
  onHighlightRef?: (index: number, element: HTMLElement | null) => void;
}

interface TextSegment {
  text: string;
  isHighlight: boolean;
  isActive: boolean;
  highlightIndex?: number;
}

/**
 * Component that renders text with highlighted search results.
 *
 * @example
 * <HighlightedText
 *   text="Document content here..."
 *   highlights={[
 *     { start: 10, end: 20, relevance: 0.9, matchedText: "content", context: "Match" }
 *   ]}
 *   activeHighlightIndex={0}
 * />
 */
export default function HighlightedText({
  text,
  highlights,
  activeHighlightIndex,
  onHighlightRef
}: HighlightedTextProps) {
  // If no highlights, just render plain text
  if (!highlights || highlights.length === 0) {
    return <div className="whitespace-pre-wrap">{text}</div>;
  }

  // Sort highlights by start position
  const sortedHighlights = [...highlights].sort((a, b) => a.start - b.start);

  // Split text into segments
  const segments: TextSegment[] = [];
  let currentIndex = 0;

  sortedHighlights.forEach((highlight, highlightIndex) => {
    const { start, end } = highlight;
    const isActive = highlightIndex === activeHighlightIndex;

    // Add text before highlight (if any)
    if (currentIndex < start) {
      segments.push({
        text: text.substring(currentIndex, start),
        isHighlight: false,
        isActive: false,
      });
    }

    // Add highlighted text
    segments.push({
      text: text.substring(start, end),
      isHighlight: true,
      isActive,
      highlightIndex,
    });

    currentIndex = end;
  });

  // Add remaining text after last highlight (if any)
  if (currentIndex < text.length) {
    segments.push({
      text: text.substring(currentIndex),
      isHighlight: false,
      isActive: false,
    });
  }

  return (
    <div className="whitespace-pre-wrap">
      {segments.map((segment, index) => {
        if (!segment.isHighlight) {
          return <React.Fragment key={index}>{segment.text}</React.Fragment>;
        }

        // Render highlighted segment
        return (
          <mark
            key={index}
            ref={(el) => {
              if (onHighlightRef && segment.highlightIndex !== undefined) {
                onHighlightRef(segment.highlightIndex, el);
              }
            }}
            className={`
              rounded-sm px-0.5 transition-all duration-200
              ${
                segment.isActive
                  ? 'bg-amber-400 dark:bg-amber-500 ring-2 ring-amber-600 dark:ring-amber-400 font-medium'
                  : 'bg-yellow-200 dark:bg-yellow-300 text-gray-900'
              }
            `}
            data-highlight-index={segment.highlightIndex}
            data-active={segment.isActive}
          >
            {segment.text}
          </mark>
        );
      })}
    </div>
  );
}
