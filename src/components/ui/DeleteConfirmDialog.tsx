/**
 * Delete Confirmation Dialog Component (S4-002)
 *
 * A reusable confirmation dialog for file deletion operations.
 * Displays a warning message and requires explicit user confirmation
 * before proceeding with the destructive action.
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
import { AlertTriangle } from 'lucide-react';

export interface DeleteConfirmDialogProps {
  /** Whether the dialog is open */
  isOpen: boolean;
  /** Name of the file to be deleted */
  fileName: string;
  /** Callback when user confirms deletion */
  onConfirm: () => void;
  /** Callback when user cancels or closes the dialog */
  onCancel: () => void;
  /** Whether deletion is in progress (shows loading state) */
  isDeleting?: boolean;
}

/**
 * DeleteConfirmDialog displays a modal confirmation before file deletion.
 *
 * Features:
 * - Warning icon and clear messaging
 * - Cancel and Delete buttons
 * - Loading state during deletion
 * - Keyboard accessible (Escape to close)
 *
 * @example
 * ```tsx
 * <DeleteConfirmDialog
 *   isOpen={showDeleteDialog}
 *   fileName="document.pdf"
 *   onConfirm={handleDelete}
 *   onCancel={() => setShowDeleteDialog(false)}
 *   isDeleting={isDeleting}
 * />
 * ```
 */
export function DeleteConfirmDialog({
  isOpen,
  fileName,
  onConfirm,
  onCancel,
  isDeleting = false,
}: DeleteConfirmDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onCancel()}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-destructive" />
            Delete File
          </DialogTitle>
          <DialogDescription className="pt-2">
            Are you sure you want to delete{' '}
            <span className="font-medium text-foreground">"{fileName}"</span>?
            <br />
            <span className="text-destructive/80">
              This action cannot be undone.
            </span>
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={onCancel}
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={onConfirm}
            disabled={isDeleting}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
