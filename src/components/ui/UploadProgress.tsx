/**
 * UploadProgress Component
 *
 * Displays upload progress for individual files with status indicators,
 * progress bar, and file information.
 */

import { FileText, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Card } from '@/components/ui/card';
import { formatFileSize } from '@/lib/fileApi';
import { cn } from '@/lib/utils';

interface UploadProgressProps {
  /** Name of the file being uploaded */
  fileName: string;

  /** Upload progress (0-100) */
  progress: number;

  /** Current upload status */
  status: 'idle' | 'uploading' | 'success' | 'error';

  /** Error message if status is 'error' */
  error?: string;

  /** File size in bytes */
  size?: number;

  /** Additional CSS classes */
  className?: string;
}

/**
 * UploadProgress component displays real-time upload progress.
 *
 * Features:
 * - Animated progress bar
 * - Status icon (uploading, success, error)
 * - File name with truncation
 * - File size display
 * - Error message display
 */
export function UploadProgress({
  fileName,
  progress,
  status,
  error,
  size,
  className,
}: UploadProgressProps) {
  // Truncate long filenames
  const truncatedName = fileName.length > 30
    ? `${fileName.slice(0, 27)}...`
    : fileName;

  // Get status icon and color
  const getStatusIcon = () => {
    switch (status) {
      case 'uploading':
        return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-destructive" />;
      default:
        return <FileText className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'success':
        return 'border-green-500/50 bg-green-50 dark:bg-green-950/20';
      case 'error':
        return 'border-destructive/50 bg-destructive/5';
      case 'uploading':
        return 'border-primary/50 bg-primary/5';
      default:
        return 'border-border';
    }
  };

  return (
    <Card
      className={cn(
        'p-3 shadow-lg border-2 transition-all duration-300 animate-in slide-in-from-bottom-2',
        getStatusColor(),
        className
      )}
    >
      <div className="flex items-start gap-3">
        {/* File Icon */}
        <div className="flex-shrink-0 mt-0.5">
          <FileText className="h-5 w-5 text-muted-foreground" />
        </div>

        {/* File Info and Progress */}
        <div className="flex-1 min-w-0">
          {/* File Name and Size */}
          <div className="flex items-center justify-between gap-2 mb-1">
            <p className="text-sm font-medium truncate" title={fileName}>
              {truncatedName}
            </p>
            <div className="flex-shrink-0">{getStatusIcon()}</div>
          </div>

          {/* File Size */}
          {size && (
            <p className="text-xs text-muted-foreground mb-2">
              {formatFileSize(size)}
            </p>
          )}

          {/* Progress Bar */}
          {status === 'uploading' && (
            <div className="space-y-1">
              <Progress value={progress} className="h-1.5" />
              <p className="text-xs text-muted-foreground text-right">
                {progress}%
              </p>
            </div>
          )}

          {/* Success Message */}
          {status === 'success' && (
            <p className="text-xs text-green-600 dark:text-green-400 font-medium">
              Upload complete
            </p>
          )}

          {/* Error Message */}
          {status === 'error' && error && (
            <p className="text-xs text-destructive font-medium line-clamp-2">
              {error}
            </p>
          )}
        </div>
      </div>
    </Card>
  );
}
