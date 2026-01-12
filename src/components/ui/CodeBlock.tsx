/**
 * CodeBlock Component
 *
 * Displays code with syntax highlighting and copy functionality.
 * Supports multiple programming languages and provides a clean,
 * professional code presentation in chat messages.
 *
 * Part of S5-009: Improved Chat Information Presentation
 */

import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from '@/hooks/use-toast';

interface CodeBlockProps {
  /** The code content to display */
  code: string;
  /** Programming language for syntax highlighting */
  language: string;
  /** Whether to show line numbers (default: false) */
  showLineNumbers?: boolean;
}

/**
 * CodeBlock component with syntax highlighting and copy button.
 *
 * Features:
 * - Syntax highlighting for multiple languages
 * - One-click copy to clipboard
 * - Language badge display
 * - Visual feedback on copy
 * - Clean, readable styling
 *
 * @example
 * <CodeBlock
 *   code="def hello():\n    print('Hello')"
 *   language="python"
 * />
 */
export default function CodeBlock({
  code,
  language,
  showLineNumbers = false,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  /**
   * Copy code to clipboard without line numbers.
   * Shows visual feedback and toast notification.
   */
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      toast({
        title: 'Code copied',
        description: 'Code has been copied to clipboard',
      });

      // Reset copied state after 2 seconds
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (error) {
      toast({
        title: 'Copy failed',
        description: 'Failed to copy code to clipboard',
        variant: 'destructive',
      });
    }
  };

  // Map common language aliases to standard names
  const normalizeLanguage = (lang: string): string => {
    const languageMap: Record<string, string> = {
      js: 'javascript',
      ts: 'typescript',
      py: 'python',
      rb: 'ruby',
      yml: 'yaml',
      sh: 'bash',
    };
    return languageMap[lang.toLowerCase()] || lang.toLowerCase();
  };

  const normalizedLanguage = normalizeLanguage(language);

  // Display name for the language badge
  const displayLanguage = language.toUpperCase();

  return (
    <div className="relative my-4 rounded-lg overflow-hidden border border-border">
      {/* Header with language badge and copy button */}
      <div className="flex items-center justify-between px-4 py-2 bg-muted/50 border-b border-border">
        <Badge variant="outline" className="text-xs font-mono">
          {displayLanguage}
        </Badge>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleCopy}
          className="h-7 px-2 text-xs"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 mr-1" />
              Copied
            </>
          ) : (
            <>
              <Copy className="w-3 h-3 mr-1" />
              Copy
            </>
          )}
        </Button>
      </div>

      {/* Code content with syntax highlighting */}
      <div className="overflow-x-auto">
        <SyntaxHighlighter
          language={normalizedLanguage}
          style={vscDarkPlus}
          showLineNumbers={showLineNumbers}
          customStyle={{
            margin: 0,
            padding: '1rem',
            fontSize: '0.875rem',
            lineHeight: '1.5',
            background: 'hsl(var(--muted))',
          }}
          codeTagProps={{
            style: {
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
            },
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}
