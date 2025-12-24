/**
 * Duplicate File Dialog Component
 *
 * A dialog that appears when a user tries to upload a file that already exists.
 * Provides options to rename the file with a unique suffix or cancel the upload.
 */

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { AlertCircle, FileText } from 'lucide-react';

export interface DuplicateFileInfo {
  /** Original file being uploaded */
  file: File;
  /** The sanitized original filename */
  originalName: string;
  /** Suggested unique filename (e.g., "document_1.pdf") */
  suggestedName: string;
  /** Target folder ID */
  folderId: string;
}

export interface DuplicateFileDialogProps {
  /** Whether the dialog is open */
  isOpen: boolean;
  /** Information about the duplicate file */
  fileInfo: DuplicateFileInfo | null;
  /** Callback when user chooses to rename and upload */
  onRename: (fileInfo: DuplicateFileInfo) => void;
  /** Callback when user cancels the upload */
  onCancel: () => void;
}

/**
 * DuplicateFileDialog displays options when uploading a file that already exists.
 *
 * Features:
 * - Shows original and suggested filenames
 * - Clear visual indication of the conflict
 * - Two options: Rename (auto-suffix) or Cancel
 * - Keyboard accessible (Escape to cancel)
 *
 * @example
 * ```tsx
 * <DuplicateFileDialog
 *   isOpen={showDuplicateDialog}
 *   fileInfo={duplicateFileInfo}
 *   onRename={handleRenameUpload}
 *   onCancel={() => setShowDuplicateDialog(false)}
 * />
 * ```
 */
export function DuplicateFileDialog({
  isOpen,
  fileInfo,
  onRename,
  onCancel,
}: DuplicateFileDialogProps) {
  if (!fileInfo) return null;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onCancel()}>
      <DialogContent className="sm:max-w-[450px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-warning" />
            File Already Exists
          </DialogTitle>
          <DialogDescription className="pt-2 space-y-3">
            <p>
              A file named{' '}
              <span className="font-medium text-foreground">
                "{fileInfo.originalName}"
              </span>{' '}
              already exists in this folder.
            </p>
            <div className="bg-muted/50 rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Current:</span>
                <span className="font-mono text-xs bg-background px-2 py-0.5 rounded">
                  {fileInfo.originalName}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <FileText className="h-4 w-4 text-primary" />
                <span className="text-muted-foreground">Rename to:</span>
                <span className="font-mono text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                  {fileInfo.suggestedName}
                </span>
              </div>
            </div>
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={onCancel}>
            Cancel Upload
          </Button>
          <Button onClick={() => onRename(fileInfo)}>
            Rename & Upload
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
