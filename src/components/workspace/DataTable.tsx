/**
 * DataTable Component
 *
 * Renders markdown-formatted tables as properly styled HTML tables.
 * Parses markdown table syntax and presents data in a clean, readable format.
 *
 * Part of S5-009: Improved Chat Information Presentation
 */

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface DataTableProps {
  /** Markdown table string to parse and render */
  markdownTable: string;
}

interface ParsedTable {
  headers: string[];
  rows: string[][];
  alignments: ('left' | 'center' | 'right')[];
}

/**
 * Parse markdown table syntax into structured data.
 *
 * Supports:
 * - Header row
 * - Separator row with alignment (---, :---, ---:, :---:)
 * - Data rows
 *
 * @param markdown - Markdown table text
 * @returns Parsed table data with headers, rows, and alignments
 */
function parseMarkdownTable(markdown: string): ParsedTable {
  const lines = markdown.trim().split('\n').filter(line => line.trim());

  if (lines.length < 2) {
    return { headers: [], rows: [], alignments: [] };
  }

  // Parse headers (first line)
  const headers = lines[0]
    .split('|')
    .map(cell => cell.trim())
    .filter(cell => cell);

  // Parse alignment from separator row (second line)
  const separatorCells = lines[1]
    .split('|')
    .map(cell => cell.trim())
    .filter(cell => cell);

  const alignments = separatorCells.map(cell => {
    const left = cell.startsWith(':');
    const right = cell.endsWith(':');

    if (left && right) return 'center';
    if (right) return 'right';
    return 'left';
  });

  // Parse data rows (remaining lines)
  const rows = lines.slice(2).map(line =>
    line
      .split('|')
      .map(cell => cell.trim())
      .filter(cell => cell !== '')
  );

  return { headers, rows, alignments };
}

/**
 * DataTable component for rendering markdown tables.
 *
 * Automatically parses markdown table syntax and renders as a
 * properly styled HTML table using shadcn table components.
 *
 * @example
 * <DataTable
 *   markdownTable="
 *     | Name | Age |
 *     | ---- | --- |
 *     | John | 30  |
 *     | Jane | 25  |
 *   "
 * />
 */
export default function DataTable({ markdownTable }: DataTableProps) {
  const { headers, rows, alignments } = parseMarkdownTable(markdownTable);

  // Don't render if parsing failed
  if (headers.length === 0) {
    return null;
  }

  /**
   * Get CSS class for text alignment based on column alignment.
   */
  const getAlignmentClass = (alignment: 'left' | 'center' | 'right'): string => {
    switch (alignment) {
      case 'center':
        return 'text-center';
      case 'right':
        return 'text-right';
      default:
        return 'text-left';
    }
  };

  return (
    <div className="my-4 rounded-lg border border-border overflow-hidden">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {headers.map((header, index) => (
                <TableHead
                  key={index}
                  className={getAlignmentClass(alignments[index] || 'left')}
                >
                  {header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <TableCell
                    key={cellIndex}
                    className={getAlignmentClass(alignments[cellIndex] || 'left')}
                  >
                    {cell}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
