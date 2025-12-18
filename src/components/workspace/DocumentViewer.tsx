import { useState } from 'react';
import { useApp } from '@/contexts/AppContext';
import { FileText, FileJson, FileCode, File, Download, Languages, EyeOff, FileOutput, Database, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { toast } from '@/hooks/use-toast';

type DocumentTab = 'pdf' | 'xml' | 'json' | 'docx';

export default function DocumentViewer() {
  const { selectedDocument, setSelectedDocument, setViewMode } = useApp();
  const [activeTab, setActiveTab] = useState<DocumentTab>('pdf');

  const tabs: { id: DocumentTab; label: string; icon: React.ReactNode }[] = [
    { id: 'pdf', label: 'PDF', icon: <FileText className="w-4 h-4" /> },
    { id: 'xml', label: 'XML', icon: <FileCode className="w-4 h-4" /> },
    { id: 'json', label: 'JSON', icon: <FileJson className="w-4 h-4" /> },
    { id: 'docx', label: 'DOCX', icon: <File className="w-4 h-4" /> },
  ];

  const documentActions = [
    { label: 'Convert PDF', icon: <FileOutput className="w-4 h-4" />, action: () => toast({ title: 'Converting to PDF...' }) },
    { label: 'Translate', icon: <Languages className="w-4 h-4" />, action: () => toast({ title: 'Translating to German...' }) },
    { label: 'Anonymize', icon: <EyeOff className="w-4 h-4" />, action: () => toast({ title: 'Anonymizing document...' }) },
    { label: 'Download', icon: <Download className="w-4 h-4" />, action: () => toast({ title: 'Downloading...' }) },
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
          <FileText className="w-4 h-4 text-primary" />
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
        {selectedDocument.type === 'txt' && selectedDocument.content ? (
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
          {documentActions.map(({ label, icon, action }) => (
            <Button key={label} variant="outline" size="sm" onClick={action} className="gap-1.5 text-xs h-8">
              {icon}
              {label}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
