import { useState, useRef, useCallback } from 'react';
import { useApp } from '@/contexts/AppContext';
import { Folder, Document } from '@/types/case';
import { ChevronRight, ChevronDown, Folder as FolderIcon, FolderOpen, FileText, FileJson, FileCode, File, Upload, Plus, MoreVertical, Loader2, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTranslation } from 'react-i18next';
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
  ContextMenuSeparator,
} from '@/components/ui/context-menu';
import { toast } from '@/hooks/use-toast';
import { loadDocumentContent } from '@/lib/documentLoader';
import { uploadFile, validateFileSize, formatFileSize, deleteFile, checkFileExists } from '@/lib/fileApi';
import type { UploadProgress } from '@/types/file';
import { UploadProgress as UploadProgressComponent } from '@/components/ui/UploadProgress';
import { DeleteConfirmDialog } from '@/components/ui/DeleteConfirmDialog';
import { DuplicateFileDialog, DuplicateFileInfo } from '@/components/ui/DuplicateFileDialog';

const getFileIcon = (type: Document['type']) => {
  switch (type) {
    case 'pdf':
      return <FileText className="w-4 h-4 text-destructive/70" />;
    case 'json':
      return <FileJson className="w-4 h-4 text-warning" />;
    case 'xml':
      return <FileCode className="w-4 h-4 text-success" />;
    case 'docx':
      return <File className="w-4 h-4 text-command-highlight" />;
    case 'txt':
      return <FileText className="w-4 h-4 text-primary" />;
    default:
      return <File className="w-4 h-4 text-muted-foreground" />;
  }
};

interface FolderItemProps {
  folder: Folder;
  level: number;
  onUploadToFolder: (folderId: string, files: File[]) => void;
  onDeleteDocument: (folderId: string, document: Document) => void;
}

function FolderItem({ folder, level, onUploadToFolder, onDeleteDocument }: FolderItemProps) {
  const { toggleFolder, selectedDocument, setSelectedDocument, setViewMode, highlightedFolder, currentCase } = useApp();
  const { t } = useTranslation();
  const [loadingDocId, setLoadingDocId] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [hoveredDocId, setHoveredDocId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isHighlighted = highlightedFolder === folder.id;

  // Check if this folder is the uploads folder (can delete files)
  const isUploadsFolder = folder.id === 'uploads' || folder.name.toLowerCase() === 'uploads';

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer?.types?.includes('Files')) {
      setIsDragOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      onUploadToFolder(folder.id, files);
    }
  };

  const handleUploadClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    fileInputRef.current?.click();
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      onUploadToFolder(folder.id, files);
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Hidden file input for upload */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={handleFileInputChange}
        className="hidden"
        accept="*/*"
      />

      <ContextMenu>
        <ContextMenuTrigger>
          <div
            className={cn(
              'tree-item transition-all duration-200',
              isHighlighted && 'bg-tree-selected ring-2 ring-command-highlight/30',
              isDragOver && 'bg-primary/20 ring-2 ring-primary border-dashed'
            )}
            style={{ paddingLeft: `${12 + level * 16}px` }}
            onClick={() => toggleFolder(folder.id)}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <span className="text-muted-foreground">
              {folder.isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </span>
            {isDragOver ? (
              <Upload className="w-4 h-4 text-primary animate-pulse" />
            ) : folder.isExpanded ? (
              <FolderOpen className="w-4 h-4 text-warning" />
            ) : (
              <FolderIcon className="w-4 h-4 text-warning" />
            )}
            <span className="flex-1 truncate">
              {isDragOver ? t('documents.dropHere') : (t(`folders.${folder.name}`, folder.name))}
            </span>
            <span className="text-xs text-muted-foreground">
              {folder.documents.length}
            </span>
          </div>
        </ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem onClick={handleUploadClick}>
            <Upload className="w-4 h-4 mr-2" />
            {t('documents.uploadDocument')}
          </ContextMenuItem>
          <ContextMenuItem>
            <Plus className="w-4 h-4 mr-2" />
            {t('documents.addSubfolder')}
          </ContextMenuItem>
          <ContextMenuSeparator />
          <ContextMenuItem>
            <MoreVertical className="w-4 h-4 mr-2" />
            {t('documents.viewMetadata')}
          </ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>

      {folder.isExpanded && (
        <div>
          {folder.documents.map((doc) => (
            <ContextMenu key={doc.id}>
              <ContextMenuTrigger>
                <div
                  className={cn(
                    'tree-item group',
                    selectedDocument?.id === doc.id && 'selected',
                    loadingDocId === doc.id && 'opacity-50'
                  )}
                  style={{ paddingLeft: `${28 + level * 16}px` }}
                  onMouseEnter={() => setHoveredDocId(doc.id)}
                  onMouseLeave={() => setHoveredDocId(null)}
                  onClick={async () => {
                    // For text files, load content from case-scoped path
                    if (doc.type === 'txt' && doc.caseId && doc.folderId) {
                      setLoadingDocId(doc.id);
                      try {
                        const content = await loadDocumentContent(
                          doc.caseId,
                          doc.folderId,
                          doc.name
                        );
                        // Set document with loaded content
                        setSelectedDocument({ ...doc, content });
                        setViewMode('document');
                        toast({
                          title: t('documents.documentLoaded'),
                          description: `${doc.name} ${t('documents.loadedSuccessfully')}`,
                        });
                      } catch (error) {
                        console.error('Failed to load document:', error);
                        toast({
                          title: t('documents.errorLoadingDocument'),
                          description: error instanceof Error ? error.message : t('documents.failedToLoadContent'),
                          variant: 'destructive',
                        });
                      } finally {
                        setLoadingDocId(null);
                      }
                    } else {
                      // For other document types, just select them
                      setSelectedDocument(doc);
                      setViewMode('document');
                    }
                  }}
                >
                  {loadingDocId === doc.id ? (
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  ) : (
                    getFileIcon(doc.type)
                  )}
                  <span className="flex-1 truncate">{doc.name}</span>
                  <span className="text-xs text-muted-foreground">{doc.size}</span>
                  {/* Delete button - only visible on hover in uploads folder */}
                  {isUploadsFolder && hoveredDocId === doc.id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteDocument(folder.id, doc);
                      }}
                      className="p-1 rounded hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors"
                      title="Delete file"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </ContextMenuTrigger>
              <ContextMenuContent>
                <ContextMenuItem onClick={() => setViewMode('document')}>
                  <FileText className="w-4 h-4 mr-2" />
                  {t('documents.viewDocument')}
                </ContextMenuItem>
                <ContextMenuItem onClick={() => setViewMode('metadata')}>
                  <MoreVertical className="w-4 h-4 mr-2" />
                  {t('documents.viewMetadata')}
                </ContextMenuItem>
                {isUploadsFolder && (
                  <>
                    <ContextMenuSeparator />
                    <ContextMenuItem
                      onClick={() => onDeleteDocument(folder.id, doc)}
                      className="text-destructive focus:text-destructive"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      {t('documents.deleteFile')}
                    </ContextMenuItem>
                  </>
                )}
              </ContextMenuContent>
            </ContextMenu>
          ))}
          {folder.subfolders.map((subfolder) => (
            <FolderItem key={subfolder.id} folder={subfolder} level={level + 1} onUploadToFolder={onUploadToFolder} onDeleteDocument={onDeleteDocument} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function CaseTreeExplorer() {
  const { currentCase, setViewMode, isSidebarCollapsed, setIsSidebarCollapsed, addDocumentToFolder, removeDocumentFromFolder } = useApp();
  const { t } = useTranslation();
  const [uploadQueue, setUploadQueue] = useState<UploadProgress[]>([]);
  const [isDraggingOverDropZone, setIsDraggingOverDropZone] = useState(false);
  const dropZoneFileInputRef = useRef<HTMLInputElement>(null);

  // Delete confirmation dialog state (S4-002)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<{ folderId: string; document: Document } | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Duplicate file dialog state
  const [duplicateDialogOpen, setDuplicateDialogOpen] = useState(false);
  const [duplicateFileInfo, setDuplicateFileInfo] = useState<DuplicateFileInfo | null>(null);
  const [pendingUploads, setPendingUploads] = useState<{ folderId: string; files: File[] }[]>([]);

  /**
   * Perform the actual upload of a single file (internal helper)
   */
  const performUpload = useCallback(async (
    folderId: string,
    file: File,
    renameTo?: string // Optional alternative filename (for duplicate handling)
  ) => {
    const displayName = renameTo || file.name;

    // Initialize upload progress
    const uploadProgress: UploadProgress = {
      fileName: displayName,
      progress: 0,
      status: 'uploading',
      size: file.size,
      startedAt: new Date(),
    };

    setUploadQueue((prev) => [...prev, uploadProgress]);

    try {
      const result = await uploadFile({
        file,
        caseId: currentCase.id,
        folderId,
        renameTo, // Pass the renamed filename to backend
        onProgress: (progress) => {
          setUploadQueue((prev) =>
            prev.map((item) =>
              item.fileName === displayName ? { ...item, progress } : item
            )
          );
        },
      });

      // Update status to success
      setUploadQueue((prev) =>
        prev.map((item) =>
          item.fileName === displayName
            ? { ...item, status: 'success', progress: 100, completedAt: new Date() }
            : item
        )
      );

      // Add document to folder in state
      const newDocument: Document = {
        id: `doc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: result.file_name,
        type: file.name.split('.').pop()?.toLowerCase() as Document['type'] || 'txt',
        size: formatFileSize(file.size),
        uploadedAt: new Date().toISOString().split('T')[0],
        caseId: currentCase.id,
        folderId: folderId,
      };

      addDocumentToFolder(currentCase.id, folderId, newDocument);

      toast({
        title: 'Upload complete',
        description: `${result.file_name} added to folder`,
      });

      // Remove from queue after delay
      setTimeout(() => {
        setUploadQueue((prev) => prev.filter((item) => item.fileName !== displayName));
      }, 3000);

    } catch (error) {
      // Update status to error
      setUploadQueue((prev) =>
        prev.map((item) =>
          item.fileName === displayName
            ? {
                ...item,
                status: 'error',
                error: error instanceof Error ? error.message : 'Upload failed',
                completedAt: new Date(),
              }
            : item
        )
      );

      toast({
        title: 'Upload failed',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive',
      });

      // Remove from queue after delay
      setTimeout(() => {
        setUploadQueue((prev) => prev.filter((item) => item.fileName !== displayName));
      }, 5000);
    }
  }, [currentCase.id, addDocumentToFolder]);

  /**
   * Process next pending upload after duplicate dialog action
   */
  const processNextPendingUpload = useCallback(async () => {
    if (pendingUploads.length === 0) return;

    const [current, ...remaining] = pendingUploads;
    setPendingUploads(remaining);

    if (current.files.length > 0) {
      // Re-trigger upload for remaining files in this batch
      handleUploadToFolder(current.folderId, current.files);
    } else if (remaining.length > 0) {
      // Process next batch
      processNextPendingUpload();
    }
  }, [pendingUploads]);

  /**
   * Upload files to a specific folder with duplicate detection
   */
  const handleUploadToFolder = useCallback(async (folderId: string, files: File[]) => {
    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      // Validate file size
      const validationError = validateFileSize(file);
      if (validationError) {
        toast({
          title: 'File too large',
          description: validationError.detail || validationError.message,
          variant: 'destructive',
        });
        continue;
      }

      // Check if file already exists (with timeout fallback)
      let shouldProceedWithUpload = true;
      try {
        // Add timeout to prevent hanging
        const timeoutPromise = new Promise<null>((_, reject) =>
          setTimeout(() => reject(new Error('Timeout')), 3000)
        );

        const existsResult = await Promise.race([
          checkFileExists(currentCase.id, folderId, file.name),
          timeoutPromise
        ]);

        if (existsResult && existsResult.exists && existsResult.suggested_name) {
          // File exists - show duplicate dialog
          setDuplicateFileInfo({
            file,
            originalName: existsResult.file_name,
            suggestedName: existsResult.suggested_name,
            folderId,
          });
          setDuplicateDialogOpen(true);

          // Store remaining files for later processing
          const remainingFiles = files.slice(i + 1);
          if (remainingFiles.length > 0) {
            setPendingUploads((prev) => [...prev, { folderId, files: remainingFiles }]);
          }

          // Stop processing this batch - will continue after dialog action
          return;
        }
      } catch (error) {
        console.warn('File existence check failed, proceeding with upload:', error);
        // If check fails or times out, proceed with upload
        shouldProceedWithUpload = true;
      }

      // Proceed with upload
      if (shouldProceedWithUpload) {
        await performUpload(folderId, file);
      }
    }
  }, [currentCase.id, performUpload]);

  /**
   * Handle rename and upload from duplicate dialog
   */
  const handleDuplicateRename = useCallback(async (fileInfo: DuplicateFileInfo) => {
    setDuplicateDialogOpen(false);

    // Create a new file with the suggested name for display purposes
    // The backend will use the suggested name
    await performUpload(fileInfo.folderId, fileInfo.file, fileInfo.suggestedName);

    setDuplicateFileInfo(null);

    // Process any remaining pending uploads
    processNextPendingUpload();
  }, [performUpload, processNextPendingUpload]);

  /**
   * Handle cancel from duplicate dialog
   */
  const handleDuplicateCancel = useCallback(() => {
    setDuplicateDialogOpen(false);
    setDuplicateFileInfo(null);

    toast({
      title: 'Upload cancelled',
      description: 'File was not uploaded',
    });

    // Process any remaining pending uploads
    processNextPendingUpload();
  }, [processNextPendingUpload]);

  /**
   * Handle delete document request - opens confirmation dialog (S4-002)
   */
  const handleDeleteDocument = useCallback((folderId: string, document: Document) => {
    setDocumentToDelete({ folderId, document });
    setDeleteDialogOpen(true);
  }, []);

  /**
   * Confirm and execute file deletion (S4-002)
   */
  const handleConfirmDelete = useCallback(async () => {
    if (!documentToDelete) return;

    const { folderId, document } = documentToDelete;
    setIsDeleting(true);

    try {
      // Call backend API to delete file
      await deleteFile(currentCase.id, folderId, document.name);

      // Remove from local state
      removeDocumentFromFolder(currentCase.id, folderId, document.id);

      toast({
        title: 'File deleted',
        description: `${document.name} has been removed`,
      });

      // Close dialog and reset state
      setDeleteDialogOpen(false);
      setDocumentToDelete(null);
    } catch (error) {
      console.error('Failed to delete file:', error);
      toast({
        title: 'Delete failed',
        description: error instanceof Error ? error.message : 'Failed to delete file',
        variant: 'destructive',
      });
    } finally {
      setIsDeleting(false);
    }
  }, [documentToDelete, currentCase.id, removeDocumentFromFolder]);

  /**
   * Cancel delete operation (S4-002)
   */
  const handleCancelDelete = useCallback(() => {
    setDeleteDialogOpen(false);
    setDocumentToDelete(null);
  }, []);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    toast({
      title: 'Drop files on a folder',
      description: 'Please drop files on a specific folder to upload',
    });
  };

  // Drop zone handlers
  const handleDropZoneDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer?.types?.includes('Files')) {
      setIsDraggingOverDropZone(true);
    }
  };

  const handleDropZoneDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOverDropZone(false);
  };

  const handleDropZoneDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOverDropZone(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      // Upload to "uploads" folder by default
      handleUploadToFolder('uploads', files);
    }
  };

  const handleDropZoneClick = () => {
    dropZoneFileInputRef.current?.click();
  };

  const handleDropZoneFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      handleUploadToFolder('uploads', files);
    }
    if (dropZoneFileInputRef.current) {
      dropZoneFileInputRef.current.value = '';
    }
  };

  if (isSidebarCollapsed) {
    return (
      <div className="w-12 border-r border-pane-border bg-pane-header/30 flex flex-col items-center py-3">
        <button
          onClick={() => setIsSidebarCollapsed(false)}
          className="p-2 hover:bg-accent rounded-lg transition-colors"
          title="Expand folder tree"
        >
          <FolderOpen className="w-5 h-5 text-primary" />
        </button>
      </div>
    );
  }

  return (
    <div
      className="pane w-64 min-w-[240px]"
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <div className="pane-header">
        <div className="flex items-center gap-2">
          <FolderOpen className="w-4 h-4 text-primary" />
          <span>{t('documents.caseExplorer')}</span>
        </div>
        <button
          onClick={() => setIsSidebarCollapsed(true)}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          title="Collapse"
        >
          ←
        </button>
      </div>

      <div className="p-2 border-b border-pane-border bg-pane-header/50">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-xs">{currentCase.id.replace(/^ACTE-/, `${t('case.prefix')}-`)}</p>
            <p className="text-xs text-muted-foreground truncate">{t(`caseTemplates.integration`, currentCase.name)}</p>
          </div>
          <span className={cn(
            'px-1.5 py-0.5 text-xs rounded-full',
            currentCase.status === 'open' && 'bg-success/10 text-success',
            currentCase.status === 'pending' && 'bg-warning/10 text-warning',
            currentCase.status === 'completed' && 'bg-primary/10 text-primary'
          )}>
            {currentCase.status}
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto py-1 scrollbar-thin">
        {currentCase.folders.map((folder) => (
          <FolderItem key={folder.id} folder={folder} level={0} onUploadToFolder={handleUploadToFolder} onDeleteDocument={handleDeleteDocument} />
        ))}
      </div>

      {/* Hidden file input for drop zone */}
      <input
        ref={dropZoneFileInputRef}
        type="file"
        multiple
        onChange={handleDropZoneFileChange}
        className="hidden"
        accept="*/*"
      />

      {/* Drop Zone Section */}
      <div className="p-2 border-t border-pane-border">
        <div
          onClick={handleDropZoneClick}
          onDragOver={handleDropZoneDragOver}
          onDragLeave={handleDropZoneDragLeave}
          onDrop={handleDropZoneDrop}
          className={cn(
            'flex items-center justify-center gap-2 p-3 border-2 border-dashed rounded-lg transition-all duration-200 cursor-pointer',
            isDraggingOverDropZone
              ? 'border-primary bg-primary/10 text-primary scale-105'
              : 'border-border text-muted-foreground hover:border-primary hover:text-primary hover:bg-primary/5'
          )}
        >
          <Upload className={cn('w-4 h-4', isDraggingOverDropZone && 'animate-bounce')} />
          <span className="text-xs font-medium">
            {isDraggingOverDropZone ? t('chat.dropToUpload') : t('chat.clickOrDrop')}
          </span>
        </div>
      </div>

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

      {/* Delete Confirmation Dialog (S4-002) */}
      <DeleteConfirmDialog
        isOpen={deleteDialogOpen}
        fileName={documentToDelete?.document.name || ''}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        isDeleting={isDeleting}
      />

      {/* Duplicate File Dialog */}
      <DuplicateFileDialog
        isOpen={duplicateDialogOpen}
        fileInfo={duplicateFileInfo}
        onRename={handleDuplicateRename}
        onCancel={handleDuplicateCancel}
      />
    </div>
  );
}
