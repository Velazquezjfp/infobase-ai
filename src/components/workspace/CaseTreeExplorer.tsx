import { useState } from 'react';
import { useApp } from '@/contexts/AppContext';
import { Folder, Document } from '@/types/case';
import { ChevronRight, ChevronDown, Folder as FolderIcon, FolderOpen, FileText, FileJson, FileCode, File, Upload, Plus, MoreVertical, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
  ContextMenuSeparator,
} from '@/components/ui/context-menu';
import { toast } from '@/hooks/use-toast';
import { loadDocumentContent } from '@/lib/documentLoader';

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
}

function FolderItem({ folder, level }: FolderItemProps) {
  const { toggleFolder, selectedDocument, setSelectedDocument, setViewMode, highlightedFolder, currentCase } = useApp();
  const [loadingDocId, setLoadingDocId] = useState<string | null>(null);
  const isHighlighted = highlightedFolder === folder.id;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.add('bg-accent');
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.currentTarget.classList.remove('bg-accent');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('bg-accent');
    toast({
      title: 'Document uploaded',
      description: `File will be added to ${folder.name}`,
    });
  };

  return (
    <div className="animate-fade-in">
      <ContextMenu>
        <ContextMenuTrigger>
          <div
            className={cn(
              'tree-item',
              isHighlighted && 'bg-tree-selected ring-2 ring-command-highlight/30'
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
            {folder.isExpanded ? (
              <FolderOpen className="w-4 h-4 text-warning" />
            ) : (
              <FolderIcon className="w-4 h-4 text-warning" />
            )}
            <span className="flex-1 truncate">{folder.name}</span>
            <span className="text-xs text-muted-foreground">
              {folder.documents.length}
            </span>
          </div>
        </ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem>
            <Upload className="w-4 h-4 mr-2" />
            Upload Document
          </ContextMenuItem>
          <ContextMenuItem>
            <Plus className="w-4 h-4 mr-2" />
            Add Subfolder
          </ContextMenuItem>
          <ContextMenuSeparator />
          <ContextMenuItem>
            <MoreVertical className="w-4 h-4 mr-2" />
            View Metadata
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
                    'tree-item',
                    selectedDocument?.id === doc.id && 'selected',
                    loadingDocId === doc.id && 'opacity-50'
                  )}
                  style={{ paddingLeft: `${28 + level * 16}px` }}
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
                          title: 'Document loaded',
                          description: `${doc.name} loaded successfully`,
                        });
                      } catch (error) {
                        console.error('Failed to load document:', error);
                        toast({
                          title: 'Error loading document',
                          description: error instanceof Error ? error.message : 'Failed to load document content',
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
                </div>
              </ContextMenuTrigger>
              <ContextMenuContent>
                <ContextMenuItem onClick={() => setViewMode('document')}>
                  <FileText className="w-4 h-4 mr-2" />
                  View Document
                </ContextMenuItem>
                <ContextMenuItem onClick={() => setViewMode('metadata')}>
                  <MoreVertical className="w-4 h-4 mr-2" />
                  View Metadata
                </ContextMenuItem>
              </ContextMenuContent>
            </ContextMenu>
          ))}
          {folder.subfolders.map((subfolder) => (
            <FolderItem key={subfolder.id} folder={subfolder} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function CaseTreeExplorer() {
  const { currentCase, setViewMode, isSidebarCollapsed, setIsSidebarCollapsed } = useApp();

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
          <span>Case Explorer</span>
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
            <p className="font-medium text-xs">{currentCase.id}</p>
            <p className="text-xs text-muted-foreground truncate">{currentCase.name}</p>
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
          <FolderItem key={folder.id} folder={folder} level={0} />
        ))}
      </div>

      <div className="p-2 border-t border-pane-border">
        <div className="flex items-center justify-center gap-2 p-3 border-2 border-dashed border-border rounded-lg text-muted-foreground hover:border-primary hover:text-primary transition-colors cursor-pointer">
          <Upload className="w-4 h-4" />
          <span className="text-xs">Drop files here</span>
        </div>
      </div>
    </div>
  );
}
