import { useState, useEffect, useRef } from 'react';
import { useApp } from '@/contexts/AppContext';
import { FileText, FileJson, FileCode, File, Download, Languages, EyeOff, FileOutput, Database, X, Loader2, ImageIcon, AlertCircle, Search, ChevronUp, ChevronDown, Eye } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { toast } from '@/hooks/use-toast';
import { AnonymizationRequest } from '@/types/websocket';
import HighlightedText from '@/components/workspace/HighlightedText';
import PDFViewer from '@/components/workspace/PDFViewer';
import EmailViewer from '@/components/workspace/EmailViewer';

type DocumentTab = 'pdf' | 'xml' | 'json' | 'docx';

// Supported image extensions for viewing
const IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];

export default function DocumentViewer() {
  const {
    selectedDocument,
    setSelectedDocument,
    setViewMode,
    wsConnection,
    wsStatus,
    currentCase,
    isAnonymizing,
    setIsAnonymizing,
    isTranslating,
    setIsTranslating,
    // S5-003: Search state
    searchQuery,
    searchHighlights,
    activeHighlightIndex,
    setActiveHighlightIndex,
    isSearching,
    performSemanticSearch,
    clearSearch,
    // S5-006: Render selection
    selectedRender,
    // S5-003: Update document content
    updateSelectedDocumentContent,
  } = useApp();

  const [activeTab, setActiveTab] = useState<DocumentTab>('pdf');
  const [imageLoading, setImageLoading] = useState(true);
  const [imageError, setImageError] = useState(false);

  // S5-003: Search dialog state
  const [searchDialogOpen, setSearchDialogOpen] = useState(false);
  const [searchInput, setSearchInput] = useState('');

  // S5-003: Refs for highlights
  const highlightRefs = useRef<(HTMLElement | null)[]>([]);

  // Document content fetching state
  const [documentContent, setDocumentContent] = useState<string>('');
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [contentError, setContentError] = useState<string | null>(null);

  // PDF view mode: 'visual' shows the PDF, 'text' shows extracted text with highlights
  const [pdfViewMode, setPdfViewMode] = useState<'visual' | 'text'>('visual');

  // S5-008: Email data state
  const [emailData, setEmailData] = useState<any>(null);
  const [isLoadingEmail, setIsLoadingEmail] = useState(false);

  // S5-006: Clear cached data when render selection changes
  useEffect(() => {
    console.log('Render changed:', {
      selectedRender,
      documentId: selectedDocument?.id,
      documentName: selectedDocument?.name,
    });
    setEmailData(null);
    setDocumentContent('');
    setImageLoading(true);
    setImageError(false);
  }, [selectedRender, selectedDocument?.id]);

  // Check if document is an image
  const isImage = selectedDocument
    ? IMAGE_EXTENSIONS.includes(selectedDocument.type?.toLowerCase() || '')
    : false;

  // S5-006: Get the active render (if one is selected)
  const activeRender = selectedDocument && selectedRender
    ? selectedDocument.renders?.find(r => r.id === selectedRender)
    : null;

  // S5-006: Use render's filePath if a render is selected, otherwise use document name
  const documentFileName = activeRender
    ? activeRender.filePath.split('/').pop() || selectedDocument?.name || ''
    : selectedDocument?.name || '';

  // Construct image path for display
  const imagePath = selectedDocument
    ? `/documents/${currentCase.id}/${selectedDocument.folderId}/${documentFileName}`
    : '';

  // Construct PDF path - handles both root_docs and case folders
  const pdfPath = selectedDocument
    ? selectedDocument.metadata?.filePath?.includes('root_docs')
      ? `http://localhost:8000/root_docs/${documentFileName}`
      : `http://localhost:8000/documents/${currentCase.id}/${selectedDocument.folderId}/${documentFileName}`
    : '';

  // Reset image state when document changes or render selection changes
  useEffect(() => {
    if (selectedDocument && isImage) {
      setImageLoading(true);
      setImageError(false);
      // S5-006: Debug log with render information
      console.log('Loading image:', {
        name: selectedDocument.name,
        selectedRender: selectedRender,
        imagePath: imagePath,
      });
    }
  }, [selectedDocument, selectedRender, isImage, currentCase.id, imagePath]);

  // Fetch content for PDFs and .eml files
  useEffect(() => {
    // S5-006: AbortController to cancel previous fetches when render changes
    const abortController = new AbortController();

    const fetchDocumentContent = async () => {
      if (!selectedDocument) {
        setDocumentContent('');
        return;
      }

      // S5-006: Recalculate active render and filename inside effect
      const activeRender = selectedRender
        ? selectedDocument.renders?.find(r => r.id === selectedRender)
        : null;

      const documentFileName = activeRender
        ? activeRender.filePath.split('/').pop() || selectedDocument.name
        : selectedDocument.name;

      console.log('Fetching content for render:', {
        selectedRender,
        activeRender: activeRender?.type,
        documentFileName,
        originalName: selectedDocument.name
      });

      const docType = selectedDocument.type.toLowerCase();

      // S5-006: Always fetch for PDFs and .eml files when render changes (ignore cached content)
      // This ensures switching between renders (original/translated) fetches fresh data
      if (docType === 'pdf' || docType === 'eml') {
        setIsLoadingContent(true);
        setContentError(null);

        try {
          const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

          if (docType === 'pdf') {
            // S5-006: Construct the correct document path using selected render if available
            // S5-003: Ensure path includes 'public/' prefix for backend filesystem access
            const documentPath = selectedDocument.metadata?.filePath?.includes('root_docs')
              ? `root_docs/${documentFileName}`
              : `public/documents/${currentCase.id}/${selectedDocument.folderId}/${documentFileName}`;

            // For PDFs, extract text using our PDF service
            const pdfResponse = await fetch(`${API_BASE_URL}/api/documents/extract-pdf-text`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                documentPath: documentPath,
              }),
              signal: abortController.signal  // S5-006: Cancel if render changes
            }).catch((err) => {
              if (err.name === 'AbortError') {
                console.log('PDF fetch aborted (render changed)');
                return null;
              }
              console.error('PDF fetch error:', err);
              return null;
            });

            if (pdfResponse && pdfResponse.ok) {
              const data = await pdfResponse.json();
              const extractedText = data.text || 'Could not extract text from PDF';
              setDocumentContent(extractedText);

              // S5-003: Store extracted text in AppContext for AI/form fill/search
              if (extractedText && extractedText !== 'Could not extract text from PDF') {
                updateSelectedDocumentContent(extractedText);
              }
            } else {
              // Fallback: show message that PDF needs to be rendered
              setDocumentContent('PDF document selected. Click "Search" to search within this PDF using semantic search.');
            }
          } else if (docType === 'eml') {
            // S5-008: Parse .eml files
            const documentPath = `public/documents/${currentCase.id}/${selectedDocument.folderId}/${documentFileName}`;

            console.log('Fetching email:', {
              documentPath,
              documentFileName,
              selectedRender,
              activeRender: activeRender?.type
            });

            setIsLoadingEmail(true);
            const emailResponse = await fetch(`${API_BASE_URL}/api/documents/parse-email`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                documentPath: documentPath,
              }),
              signal: abortController.signal  // S5-006: Cancel if render changes
            }).catch((err) => {
              if (err.name === 'AbortError') {
                console.log('Email fetch aborted (render changed)');
                return null;
              }
              console.error('Email fetch error:', err);
              return null;
            });

            if (emailResponse && emailResponse.ok) {
              const data = await emailResponse.json();
              setEmailData(data);
              // Also store email body as content for AI context
              updateSelectedDocumentContent(data.body_text);
              setDocumentContent(data.body_text);
            } else {
              setDocumentContent('Failed to parse email file.');
              setEmailData(null);
            }
            setIsLoadingEmail(false);
          }
        } catch (error) {
          console.error('Error fetching document content:', error);
          setContentError('Failed to load document content');
          setDocumentContent('');
        } finally {
          setIsLoadingContent(false);
        }
      } else if (selectedDocument.content) {
        // Use existing content if available
        setDocumentContent(selectedDocument.content);
        setIsLoadingContent(false);
        setContentError(null);
      } else {
        // For other types or if content exists
        setDocumentContent('');
        setIsLoadingContent(false);
        setContentError(null);
      }
    };

    fetchDocumentContent().catch((err) => {
      // Ignore abort errors (expected when render changes)
      if (err?.name !== 'AbortError') {
        console.error('fetchDocumentContent error:', err);
      }
    });

    // S5-006: Cleanup function to abort fetch if render changes
    return () => {
      abortController.abort();
    };
  }, [selectedDocument?.id, selectedDocument?.type, selectedRender, currentCase.id]);
  // Note: Using selectedDocument.id instead of full object to prevent infinite loop
  // updateSelectedDocumentContent modifies selectedDocument, so we can't depend on it

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
    const filePath = `public/documents/${currentCase.id}/${selectedDocument.folderId}/${selectedDocument.name}`;

    setIsAnonymizing(true);
    toast({ title: 'Anonymizing document...', description: 'This may take a moment' });

    // S5-006: Send anonymization request via WebSocket with documentId for render registration
    const request: AnonymizationRequest = {
      type: 'anonymize',
      filePath,
      caseId: currentCase.id,
      folderId: selectedDocument.folderId || 'uploads',
      documentId: selectedDocument.id, // S5-006: Include documentId for render registration
    };

    wsConnection.send(JSON.stringify(request));
  };

  // S5-004/S5-008: Handle translation request
  const handleTranslate = (targetLang: string = 'de') => {
    if (!selectedDocument) {
      toast({ title: 'No document selected', variant: 'destructive' });
      return;
    }

    if (!wsConnection || wsStatus !== 'connected') {
      toast({ title: 'Not connected', description: 'Please wait for connection to be established', variant: 'destructive' });
      return;
    }

    // Build file path - use selected render's path if applicable
    const activeRender = selectedRender
      ? selectedDocument.renders?.find(r => r.id === selectedRender)
      : null;

    const documentFileName = activeRender
      ? activeRender.filePath.split('/').pop() || selectedDocument.name
      : selectedDocument.name;

    const filePath = `public/documents/${currentCase.id}/${selectedDocument.folderId}/${documentFileName}`;

    setIsTranslating(true);
    toast({ title: 'Translating document...', description: `Translating to ${targetLang.toUpperCase()}` });

    // S5-004/S5-006: Send translation request via WebSocket with documentId for render registration
    const request = {
      type: 'translate',
      filePath,
      caseId: currentCase.id,
      folderId: selectedDocument.folderId,
      documentId: selectedDocument.id,
      targetLanguage: targetLang,
      sourceLanguage: 'auto',
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

  // S5-003: Handle search submission
  const handleSearchSubmit = async () => {
    if (!searchInput.trim() || !selectedDocument) return;

    await performSemanticSearch(searchInput.trim(), selectedDocument.id);
    setSearchDialogOpen(false);
  };

  // S5-003: Handle search navigation
  const handleNextHighlight = () => {
    if (activeHighlightIndex < searchHighlights.length - 1) {
      const newIndex = activeHighlightIndex + 1;
      setActiveHighlightIndex(newIndex);
      scrollToHighlight(newIndex);
    }
  };

  const handlePrevHighlight = () => {
    if (activeHighlightIndex > 0) {
      const newIndex = activeHighlightIndex - 1;
      setActiveHighlightIndex(newIndex);
      scrollToHighlight(newIndex);
    }
  };

  // S5-003: Scroll to highlight
  const scrollToHighlight = (index: number) => {
    const element = highlightRefs.current[index];
    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
    }
  };

  // S5-003: Handle highlight ref callback
  const handleHighlightRef = (index: number, element: HTMLElement | null) => {
    highlightRefs.current[index] = element;
  };

  // S5-003: Keyboard shortcut for search (Ctrl+F)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        if (selectedDocument) {
          setSearchDialogOpen(true);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedDocument]);

  const isPdf = selectedDocument?.type.toLowerCase() === 'pdf';

  const documentActions = [
    // S5-003: Search button
    { label: 'Search', icon: <Search className="w-4 h-4" />, action: () => setSearchDialogOpen(true) },
    // PDF view toggle
    ...(isPdf ? [{
      label: pdfViewMode === 'visual' ? 'Text View' : 'PDF View',
      icon: <Eye className="w-4 h-4" />,
      action: () => setPdfViewMode(prev => prev === 'visual' ? 'text' : 'visual')
    }] : []),
    { label: 'Convert PDF', icon: <FileOutput className="w-4 h-4" />, action: () => toast({ title: 'Converting to PDF...' }) },
    // S5-004/S5-008: Translation button
    {
      label: isTranslating ? 'Translating...' : 'Translate',
      icon: isTranslating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Languages className="w-4 h-4" />,
      action: () => handleTranslate('de'),
      disabled: isTranslating
    },
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

      {/* S5-003: Search Results Indicator */}
      {searchHighlights.length > 0 && (
        <div className="px-4 py-2 bg-yellow-50 dark:bg-yellow-900/20 border-b border-yellow-200 dark:border-yellow-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
              {searchHighlights.length} {searchHighlights.length === 1 ? 'match' : 'matches'} found for "{searchQuery}"
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearSearch}
              className="h-6 text-xs text-yellow-700 dark:text-yellow-300 hover:text-yellow-900 dark:hover:text-yellow-100"
            >
              <X className="w-3 h-3 mr-1" />
              Clear
            </Button>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-xs text-yellow-700 dark:text-yellow-300 mr-2">
              {activeHighlightIndex + 1} of {searchHighlights.length}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrevHighlight}
              disabled={activeHighlightIndex === 0}
              className="h-6 w-6 p-0"
            >
              <ChevronUp className="w-3 h-3" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNextHighlight}
              disabled={activeHighlightIndex === searchHighlights.length - 1}
              className="h-6 w-6 p-0"
            >
              <ChevronDown className="w-3 h-3" />
            </Button>
          </div>
        </div>
      )}

      {/* Document Preview */}
      <div className="flex-1 overflow-auto">
        {selectedDocument.type === 'eml' && emailData ? (
          // S5-008: Email display
          // S5-006: Key forces re-render when switching between renders
          <EmailViewer
            key={`${selectedDocument.id}-${selectedRender || 'original'}`}
            emailData={emailData}
          />
        ) : selectedDocument.type === 'eml' && isLoadingEmail ? (
          // Loading email
          <div className="bg-muted/50 rounded-lg p-6 min-h-[300px] flex items-center justify-center border border-border h-full">
            <div className="text-center">
              <Loader2 className="w-12 h-12 mx-auto mb-3 text-primary animate-spin" />
              <p className="font-medium text-foreground mb-1">Loading Email</p>
              <p className="text-sm text-muted-foreground">Parsing email content...</p>
            </div>
          </div>
        ) : isPdf && pdfViewMode === 'visual' && searchHighlights.length === 0 ? (
          // PDF Visual View (when no search active)
          // S5-006: Key forces re-render when switching between renders
          <PDFViewer
            key={`${selectedDocument.id}-${selectedRender || 'original'}`}
            file={pdfPath}
            highlights={searchHighlights}
            activeHighlightIndex={activeHighlightIndex}
          />
        ) : isImage ? (
          // Image file display
          <div className="bg-muted/30 rounded-lg border border-border h-full flex items-center justify-center relative p-4">
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
                key={`${selectedDocument.id}-${selectedRender || 'original'}`}
                src={imagePath}
                alt={selectedDocument.name}
                className="max-w-full max-h-full object-contain rounded-lg shadow-md"
                onLoad={handleImageLoad}
                onError={handleImageError}
              />
            )}
          </div>
        ) : isLoadingContent ? (
          // Loading document content (PDF, .eml, etc.)
          <div className="bg-muted/50 rounded-lg p-6 min-h-[300px] flex items-center justify-center border border-border h-full">
            <div className="text-center">
              <Loader2 className="w-12 h-12 mx-auto mb-3 text-primary animate-spin" />
              <p className="font-medium text-foreground mb-1">Loading {selectedDocument.name}</p>
              <p className="text-sm text-muted-foreground">Extracting document content...</p>
            </div>
          </div>
        ) : contentError ? (
          // Error loading content
          <div className="bg-muted/50 rounded-lg p-6 min-h-[300px] flex items-center justify-center border border-border h-full">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 mx-auto mb-3 text-destructive" />
              <p className="font-medium text-foreground mb-1">Error Loading Document</p>
              <p className="text-sm text-muted-foreground mb-2">{contentError}</p>
              <p className="text-xs text-muted-foreground">Try selecting the document again</p>
            </div>
          </div>
        ) : documentContent || selectedDocument.content ? (
          // Text content display with optional highlighting (for txt, pdf text view, eml)
          <div className="bg-background rounded-lg border border-border h-full overflow-auto p-4">
            {isPdf && searchHighlights.length > 0 && (
              <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded">
                <p className="text-sm text-yellow-900 dark:text-yellow-100 font-medium">
                  📄 Viewing extracted text with highlights
                </p>
                <p className="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
                  Switch back to "PDF View" to see the original document layout
                </p>
              </div>
            )}
            <pre className="whitespace-pre-wrap font-mono text-sm p-2 leading-relaxed text-foreground">
              {searchHighlights.length > 0 ? (
                <HighlightedText
                  text={documentContent || selectedDocument.content || ''}
                  highlights={searchHighlights}
                  activeHighlightIndex={activeHighlightIndex}
                  onHighlightRef={handleHighlightRef}
                />
              ) : (
                documentContent || selectedDocument.content
              )}
            </pre>
          </div>
        ) : (
          // Other document types - show placeholder
          <div className="bg-muted/50 rounded-lg p-6 min-h-[300px] flex items-center justify-center border border-border h-full">
            <div className="text-center">
              <FileText className="w-12 h-12 mx-auto mb-3 text-muted-foreground" />
              <p className="font-medium text-foreground mb-1">{selectedDocument.name}</p>
              <p className="text-sm text-muted-foreground mb-2">{activeTab.toUpperCase()} Document • {selectedDocument.size}</p>
              <p className="text-xs text-muted-foreground">
                {selectedDocument.type === 'pdf' ? 'Click "Search" to search within this PDF' : 'Document preview not available'}
              </p>
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

      {/* S5-003: Search Dialog */}
      <Dialog open={searchDialogOpen} onOpenChange={setSearchDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Search in Document</DialogTitle>
            <DialogDescription>
              Enter your search query. Supports natural language and cross-language search.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Input
                placeholder="Enter search query (e.g., 'passport number', 'birth date')"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSearchSubmit();
                  }
                }}
                autoFocus
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Try natural language queries like "when was the person born" or cross-language searches.
              </p>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setSearchDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSearchSubmit}
              disabled={!searchInput.trim() || isSearching}
            >
              {isSearching ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
