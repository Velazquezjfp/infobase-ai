/**
 * FileDropZone Component
 *
 * Drag-and-drop file upload zone for the BAMF AI Case Management System.
 * Supports multiple files, progress tracking, and size validation (S4-001).
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { Upload, X, FileText, MousePointerClick } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { uploadFile, validateFileSize, formatFileSize, checkUploadEnabled } from '@/lib/fileApi';
import type { UploadProgress } from '@/types/file';
import { UploadProgress as UploadProgressComponent } from '@/components/ui/UploadProgress';

interface FileDropZoneProps {
  /** Case ID where files should be uploaded */
  caseId: string;

  /** Target folder ID (default: "uploads") */
  folderId?: string;

  /** Callback when upload completes successfully */
  onUploadComplete?: (fileName: string, filePath: string) => void;

  /** Callback when all uploads complete */
  onAllUploadsComplete?: () => void;

  /** Additional CSS classes */
  className?: string;

  /** Whether the drop zone is visible */
  isVisible?: boolean;

  /** Show click-to-upload hint */
  showClickHint?: boolean;
}

/**
 * FileDropZone component for drag-and-drop file uploads.
 *
 * Features:
 * - Visual drag-over indicator
 * - Multiple file support
 * - Progress tracking per file
 * - Client-side size validation (15 MB)
 * - Sequential upload queue
 * - Toast notifications for success/error
 */
export function FileDropZone({
  caseId,
  folderId = 'uploads',
  onUploadComplete,
  onAllUploadsComplete,
  className,
  isVisible = true,
  showClickHint = true,
}: FileDropZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isHovering, setIsHovering] = useState(false);
  const [uploadQueue, setUploadQueue] = useState<UploadProgress[]>([]);
  // S001-F-006: feature flag — fail-permissive while loading; backend enforces.
  const [uploadEnabled, setUploadEnabled] = useState<boolean>(true);
  const dragCounter = useRef(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const { t } = useTranslation();

  useEffect(() => {
    let cancelled = false;
    checkUploadEnabled().then((enabled) => {
      if (!cancelled) setUploadEnabled(enabled);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  /**
   * Global drag detection to show drop zone when files are dragged into window.
   */
  useEffect(() => {
    const handleWindowDragEnter = (e: DragEvent) => {
      // Check if dragging files (not text or other drag operations)
      if (e.dataTransfer?.types?.includes('Files')) {
        dragCounter.current++;
        setIsDragging(true);
      }
    };

    const handleWindowDragLeave = (e: DragEvent) => {
      dragCounter.current--;
      if (dragCounter.current === 0) {
        setIsDragging(false);
      }
    };

    const handleWindowDrop = (e: DragEvent) => {
      dragCounter.current = 0;
      setIsDragging(false);
    };

    const handleWindowDragOver = (e: DragEvent) => {
      // Prevent default to allow drop
      if (e.dataTransfer?.types?.includes('Files')) {
        e.preventDefault();
      }
    };

    window.addEventListener('dragenter', handleWindowDragEnter);
    window.addEventListener('dragleave', handleWindowDragLeave);
    window.addEventListener('drop', handleWindowDrop);
    window.addEventListener('dragover', handleWindowDragOver);

    return () => {
      window.removeEventListener('dragenter', handleWindowDragEnter);
      window.removeEventListener('dragleave', handleWindowDragLeave);
      window.removeEventListener('drop', handleWindowDrop);
      window.removeEventListener('dragover', handleWindowDragOver);
    };
  }, []);

  /**
   * Handle drag enter event.
   */
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  /**
   * Handle drag over event.
   */
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  /**
   * Handle drag leave event.
   */
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  /**
   * Handle drop event.
   */
  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();

      setIsDragging(false);
      dragCounter.current = 0;

      const files = Array.from(e.dataTransfer.files);

      if (files.length === 0) {
        return;
      }

      // Upload files sequentially
      await uploadFiles(files);
    },
    [caseId, folderId, onUploadComplete, onAllUploadsComplete]
  );

  /**
   * Handle click event - open file picker.
   */
  const handleClick = useCallback(() => {
    // S001-F-006: short-circuit when upload feature is disabled.
    if (!uploadEnabled) {
      toast({
        title: t('upload.notImplemented'),
      });
      return;
    }
    fileInputRef.current?.click();
  }, [uploadEnabled, t, toast]);

  /**
   * Handle file input change.
   */
  const handleFileInputChange = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files || []);

      if (files.length === 0) {
        return;
      }

      // Upload files sequentially
      await uploadFiles(files);

      // Reset input so same file can be selected again
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
    [caseId, folderId, onUploadComplete, onAllUploadsComplete]
  );

  /**
   * Upload multiple files sequentially.
   */
  const uploadFiles = async (files: File[]) => {
    // S001-F-006: when the feature flag is off, no files are sent to the
    // backend — surface the disabled-state notice and return.
    if (!uploadEnabled) {
      toast({
        title: t('upload.notImplemented'),
      });
      return;
    }

    let successCount = 0;
    let errorCount = 0;

    for (const file of files) {
      // Validate file size before upload
      const validationError = validateFileSize(file);
      if (validationError) {
        toast({
          title: 'File too large',
          description: validationError.detail || validationError.message,
          variant: 'destructive',
        });
        errorCount++;
        continue;
      }

      // Initialize upload progress
      const uploadProgress: UploadProgress = {
        fileName: file.name,
        progress: 0,
        status: 'uploading',
        size: file.size,
        startedAt: new Date(),
      };

      // Add to upload queue
      setUploadQueue((prev) => [...prev, uploadProgress]);

      try {
        // Upload file with progress tracking
        const result = await uploadFile({
          file,
          caseId,
          folderId,
          onProgress: (progress) => {
            setUploadQueue((prev) =>
              prev.map((item) =>
                item.fileName === file.name
                  ? { ...item, progress }
                  : item
              )
            );
          },
        });

        // Update status to success
        setUploadQueue((prev) =>
          prev.map((item) =>
            item.fileName === file.name
              ? { ...item, status: 'success', progress: 100, completedAt: new Date() }
              : item
          )
        );

        successCount++;

        // Show success toast
        toast({
          title: 'Upload complete',
          description: `${file.name} (${formatFileSize(file.size)})`,
        });

        // Callback
        if (onUploadComplete) {
          onUploadComplete(result.fileName, result.filePath);
        }

        // Remove from queue after delay
        setTimeout(() => {
          setUploadQueue((prev) => prev.filter((item) => item.fileName !== file.name));
        }, 3000);
      } catch (error) {
        // Update status to error
        setUploadQueue((prev) =>
          prev.map((item) =>
            item.fileName === file.name
              ? {
                  ...item,
                  status: 'error',
                  error: error instanceof Error ? error.message : 'Upload failed',
                  completedAt: new Date(),
                }
              : item
          )
        );

        errorCount++;

        // Show error toast
        toast({
          title: 'Upload failed',
          description: error instanceof Error ? error.message : 'Unknown error',
          variant: 'destructive',
        });

        // Remove from queue after delay
        setTimeout(() => {
          setUploadQueue((prev) => prev.filter((item) => item.fileName !== file.name));
        }, 5000);
      }
    }

    // All uploads complete callback
    if (onAllUploadsComplete && (successCount > 0 || errorCount > 0)) {
      onAllUploadsComplete();
    }

    // Summary toast for multiple files
    if (files.length > 1) {
      if (successCount > 0 && errorCount === 0) {
        toast({
          title: 'All uploads complete',
          description: `Successfully uploaded ${successCount} file${successCount > 1 ? 's' : ''}`,
        });
      } else if (successCount > 0 && errorCount > 0) {
        toast({
          title: 'Uploads complete with errors',
          description: `${successCount} succeeded, ${errorCount} failed`,
          variant: 'destructive',
        });
      }
    }
  };

  if (!isVisible) {
    return null;
  }

  return (
    <>
      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={handleFileInputChange}
        className="hidden"
        accept="*/*"
      />

      {/* Drop Zone Overlay - only blocks interaction when dragging */}
      <div
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          'absolute inset-0 flex flex-col items-center justify-center transition-all duration-200',
          isDragging
            ? 'z-50 bg-primary/10 backdrop-blur-sm border-4 border-dashed border-primary pointer-events-auto'
            : 'z-0 pointer-events-none',
          className
        )}
      >
        {isDragging && (
          <div className="flex flex-col items-center gap-4 pointer-events-none">
            <div className="rounded-full bg-primary/20 p-6">
              <Upload className="h-12 w-12 text-primary" />
            </div>
            <div className="text-center">
              <p className="text-xl font-semibold text-primary">Drop files here</p>
              <p className="text-sm text-muted-foreground mt-1">
                Maximum file size: 15 MB
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Click-to-Upload Button (bottom-right corner) */}
      {showClickHint && !isDragging && uploadQueue.length === 0 && (
        <button
          onClick={handleClick}
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
          aria-disabled={!uploadEnabled}
          disabled={!uploadEnabled}
          className={cn(
            'fixed bottom-6 right-6 z-40 rounded-full shadow-lg transition-all duration-300',
            'p-4 flex items-center gap-2',
            uploadEnabled
              ? 'bg-primary hover:bg-primary/90 text-primary-foreground hover:scale-110 active:scale-95'
              : 'bg-muted text-muted-foreground cursor-not-allowed opacity-60'
          )}
          title={uploadEnabled ? 'Upload files' : t('upload.notImplemented')}
        >
          <Upload className="h-5 w-5" />
          {isHovering && (
            <span className="text-sm font-medium whitespace-nowrap animate-in slide-in-from-right-2">
              {uploadEnabled ? 'Upload Files' : t('upload.notImplemented')}
            </span>
          )}
        </button>
      )}

      {/* Upload Progress Indicators */}
      {uploadQueue.length > 0 && (
        <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md">
          {uploadQueue.map((upload) => (
            <UploadProgressComponent
              key={upload.fileName}
              fileName={upload.fileName}
              progress={upload.progress}
              status={upload.status}
              error={upload.error}
              size={upload.size}
            />
          ))}
        </div>
      )}
    </>
  );
}
