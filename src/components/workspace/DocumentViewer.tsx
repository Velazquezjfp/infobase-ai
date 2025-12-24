import { useState, useEffect } from 'react';
import { useApp } from '@/contexts/AppContext';
import { FileText, FileJson, FileCode, File, Download, Languages, EyeOff, FileOutput, Database, X, Loader2, ImageIcon, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { toast } from '@/hooks/use-toast';
import { AnonymizationRequest } from '@/types/websocket';

type DocumentTab = 'pdf' | 'xml' | 'json' | 'docx';

// Supported image extensions for viewing
const IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];

export default function DocumentViewer() {
  const { selectedDocument, setSelectedDocument, setViewMode, wsConnection, wsStatus, currentCase, isAnonymizing, setIsAnonymizing } = useApp();
  const [activeTab, setActiveTab] = useState<DocumentTab>('pdf');
  const [imageLoading, setImageLoading] = useState(true);
  const [imageError, setImageError] = useState(false);

  // Check if document is an image
  const isImage = selectedDocument
    ? IMAGE_EXTENSIONS.includes(selectedDocument.type?.toLowerCase() || '')
    : false;

  // Construct image path for display
  const imagePath = selectedDocument
    ? `/documents/${currentCase.id}/${selectedDocument.folderId}/${selectedDocument.name}`
    : '';

  // Reset image state when document changes
  useEffect(() => {
    if (selectedDocument && isImage) {
      setImageLoading(true);
      setImageError(false);
      // Debug: Log image path for troubleshooting
      console.log('Loading image:', {
        name: selectedDocument.name,
        caseId: currentCase.id,
        folderId: selectedDocument.folderId,
        fullPath: `/documents/${currentCase.id}/${selectedDocument.folderId}/${selectedDocument.name}`,
      });
    }
  }, [selectedDocument?.id, isImage, currentCase.id]);

  const tabs: { id: DocumentTab; label: string; icon: React.ReactNode }[] = [
    { id: 'pdf', label: 'PDF', icon: <FileText className="w-4 h-4" /> },
    { id: 'xml', label: 'XML', icon: <FileCode className="w-4 h-4" /> },
    { id: 'json', label: 'JSON', icon: <FileJson className="w-4 h-4" /> },
    { id: 'docx', label: 'DOCX', icon: <File className="w-4 h-4" /> },
  ];

  // Handle anonymization request
  const handleAnonymize = () => {
    if (!selectedDocument) {
      toast({ title: 'No document selected', variant: 'destructive' });
      return;
    }

    if (!wsConnection || wsStatus !== 'connected') {
      toast({ title: 'Not connected', description: 'Please wait for connection to be established', variant: 'destructive' });
      return;
    }

    // Check if document is an image (supported for anonymization)
    const supportedExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'];
    const docName = selectedDocument.name.toLowerCase();
    const isImage = supportedExtensions.some(ext => docName.endsWith(ext));

    if (!isImage) {
      toast({
        title: 'Unsupported format',
        description: 'Only image files (PNG, JPG, etc.) can be anonymized',
        variant: 'destructive'
      });
      return;
    }

    // Build file path from case, folder, and document
    // Assumes documents are stored at: public/documents/{caseId}/{folderId}/{filename}
    const filePath = `public/documents/${currentCase.id}/${selectedDocument.id}/${selectedDocument.name}`;

    setIsAnonymizing(true);
    toast({ title: 'Anonymizing document...', description: 'This may take a moment' });

    // Send anonymization request via WebSocket
    const request: AnonymizationRequest = {
      type: 'anonymize',
      filePath,
      caseId: currentCase.id,
      folderId: selectedDocument.id,
    };

    wsConnection.send(JSON.stringify(request));
  };

  // Handle image download
  const handleDownloadImage = async () => {
    if (!selectedDocument || !isImage) return;

    try {
      toast({ title: 'Starting download...', description: selectedDocument.name });

      const response = await fetch(imagePath);
      if (!response.ok) {
        throw new Error('Failed to fetch image');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = selectedDocument.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({ title: 'Download complete', description: selectedDocument.name });
    } catch (error) {
      console.error('Download failed:', error);
      toast({
        title: 'Download failed',
        description: 'Could not download the image',
        variant: 'destructive'
      });
    }
  };

  // Reset image state when document changes
  const handleImageLoad = () => {
    setImageLoading(false);
    setImageError(false);
  };

  const handleImageError = () => {
    setImageLoading(false);
    setImageError(true);
  };

  const documentActions = [
    { label: 'Convert PDF', icon: <FileOutput className="w-4 h-4" />, action: () => toast({ title: 'Converting to PDF...' }) },
    { label: 'Translate', icon: <Languages className="w-4 h-4" />, action: () => toast({ title: 'Translating to German...' }) },
    {
      label: isAnonymizing ? 'Anonymizing...' : 'Anonymize',
      icon: isAnonymizing ? <Loader2 className="w-4 h-4 animate-spin" /> : <EyeOff className="w-4 h-4" />,
      action: handleAnonymize,
      disabled: isAnonymizing
    },
    { label: 'Download', icon: <Download className="w-4 h-4" />, action: isImage ? handleDownloadImage : () => toast({ title: 'Downloading...' }) },
    { label: 'Metadata', icon: <Database className="w-4 h-4" />, action: () => setViewMode('metadata') },
  ];

  if (!selectedDocument) {
    return null;
  }

  return (
    <div className="h-full w-full flex flex-col border-l border-pane-border bg-background">
      {/* Header */}
      <div className="pane-header border-b border-pane-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isImage ? (
            <ImageIcon className="w-4 h-4 text-primary" />
          ) : (
            <FileText className="w-4 h-4 text-primary" />
          )}
          <span className="font-medium truncate max-w-[200px]">{selectedDocument.name}</span>
        </div>
        <button
          onClick={() => setSelectedDocument(null)}
          className="p-1 hover:bg-accent rounded transition-colors"
        >
          <X className="w-4 h-4 text-muted-foreground" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-pane-border bg-pane-header/30">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn('tab-button flex items-center gap-2', activeTab === tab.id && 'active')}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Document Preview */}
      <div className="flex-1 p-4 overflow-auto">
        {isImage ? (
          // Image file display
          <div className="bg-muted/30 rounded-lg border border-border h-full flex items-center justify-center relative">
            {imageLoading && !imageError && (
              <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-10">
                <div className="text-center">
                  <Loader2 className="w-8 h-8 mx-auto mb-2 animate-spin text-primary" />
                  <p className="text-sm text-muted-foreground">Loading image...</p>
                </div>
              </div>
            )}
            {imageError ? (
              <div className="text-center p-6">
                <AlertCircle className="w-12 h-12 mx-auto mb-3 text-destructive" />
                <p className="font-medium text-foreground mb-1">Failed to load image</p>
                <p className="text-sm text-muted-foreground mb-2">{selectedDocument.name}</p>
                <p className="text-xs text-muted-foreground">The image could not be loaded. Check if the file exists.</p>
              </div>
            ) : (
              <img
                src={imagePath}
                alt={selectedDocument.name}
                className="max-w-full max-h-full object-contain rounded-lg shadow-md"
                onLoad={handleImageLoad}
                onError={handleImageError}
              />
            )}
          </div>
        ) : selectedDocument.type === 'txt' && selectedDocument.content ? (
          // Text file content display
          <div className="bg-background rounded-lg border border-border h-full overflow-auto">
            <pre className="whitespace-pre-wrap font-mono text-sm p-6 leading-relaxed text-foreground">
              {selectedDocument.content}
            </pre>
          </div>
        ) : selectedDocument.type === 'txt' && !selectedDocument.content ? (
          // Text file without content (loading or error)
          <div className="bg-muted/50 rounded-lg p-6 min-h-[300px] flex items-center justify-center border border-border h-full">
            <div className="text-center">
              <FileText className="w-12 h-12 mx-auto mb-3 text-muted-foreground" />
              <p className="font-medium text-foreground mb-1">{selectedDocument.name}</p>
              <p className="text-sm text-muted-foreground mb-2">Text Document • {selectedDocument.size}</p>
              <p className="text-xs text-muted-foreground">Loading document content...</p>
            </div>
          </div>
        ) : (
          // Other document types - show placeholder
          <div className="bg-muted/50 rounded-lg p-6 min-h-[300px] flex items-center justify-center border border-border h-full">
            <div className="text-center">
              <FileText className="w-12 h-12 mx-auto mb-3 text-muted-foreground" />
              <p className="font-medium text-foreground mb-1">{selectedDocument.name}</p>
              <p className="text-sm text-muted-foreground mb-2">{activeTab.toUpperCase()} Rendition • {selectedDocument.size}</p>
              <p className="text-xs text-muted-foreground">Document preview renders here</p>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-3 border-t border-pane-border bg-pane-header/30">
        <div className="flex flex-wrap gap-1.5">
          {documentActions.map(({ label, icon, action, disabled }) => (
            <Button
              key={label}
              variant="outline"
              size="sm"
              onClick={action}
              disabled={disabled}
              className="gap-1.5 text-xs h-8"
            >
              {icon}
              {label}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
