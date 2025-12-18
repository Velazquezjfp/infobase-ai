import { useApp } from '@/contexts/AppContext';
import { ClipboardList, Sparkles, Database } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/hooks/use-toast';

interface FormViewerProps {
  showMetadata?: boolean;
}

export default function FormViewer({ showMetadata = false }: FormViewerProps) {
  const { selectedDocument, formFields, updateFormField, currentCase, viewMode } = useApp();

  const renderMetadataView = () => {
    const metadata = selectedDocument?.metadata || {
      createdAt: '2024-01-15T10:30:00Z',
      importedFrom: 'Manual Upload',
      documentType: 'Certificate',
      language: 'German',
      fileSize: '245 KB',
      pages: '1',
    };

    return (
      <div className="flex-1 flex flex-col">
        <div className="p-4 border-b border-pane-border bg-accent/30">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-primary" />
            <h3 className="font-semibold text-foreground">Document Metadata</h3>
          </div>
          <p className="text-sm text-muted-foreground">{selectedDocument?.name || 'No document selected'}</p>
        </div>

        <div className="flex-1 p-4 overflow-y-auto scrollbar-thin">
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            {Object.entries(metadata).map(([key, value]) => (
              <div key={key} className="metadata-row px-4">
                <span className="text-muted-foreground capitalize min-w-[120px] text-sm">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </span>
                <span className="text-foreground font-medium text-sm">{value}</span>
              </div>
            ))}
          </div>

          <div className="mt-4">
            <h4 className="text-sm font-medium text-foreground mb-2">Add Custom Field</h4>
            <div className="flex gap-2">
              <Input placeholder="Field name" className="flex-1 h-8 text-sm" />
              <Input placeholder="Value" className="flex-1 h-8 text-sm" />
              <Button size="sm" className="h-8" onClick={() => toast({ title: 'Field added' })}>Add</Button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderFormView = () => {
    const filledFields = formFields.filter(f => f.value).length;
    const totalFields = formFields.length;

    return (
      <div className="flex-1 flex flex-col">
        <div className="p-3 border-b border-pane-border bg-accent/30">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-foreground text-sm">{currentCase.name}</h3>
              <p className="text-xs text-muted-foreground">{currentCase.id}</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="text-right">
                <p className="text-xs font-medium">{filledFields}/{totalFields}</p>
                <p className="text-xs text-muted-foreground">filled</p>
              </div>
              <div className="w-12 h-1.5 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-success transition-all"
                  style={{ width: `${(filledFields / totalFields) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1 p-4 overflow-y-auto scrollbar-thin">
          <div className="space-y-4">
            <div className="flex items-center gap-2 p-2 bg-accent/50 rounded-lg border border-border text-xs">
              <Sparkles className="w-3.5 h-3.5 text-command-highlight flex-shrink-0" />
              <p className="text-muted-foreground">
                AI can auto-fill from documents. Use chat to update fields.
              </p>
            </div>

            {formFields.map((field) => (
              <div key={field.id} className="space-y-1.5">
                <label className="block text-sm font-medium text-foreground">
                  {field.label}
                  {field.required && <span className="text-destructive ml-1">*</span>}
                </label>
                {field.type === 'text' && (
                  <Input
                    value={field.value}
                    onChange={(e) => updateFormField(field.id, e.target.value)}
                    placeholder={`Enter ${field.label.toLowerCase()}`}
                    className={cn('h-9', field.value && 'border-success/50 bg-success/5')}
                  />
                )}
                {field.type === 'date' && (
                  <Input
                    type="date"
                    value={field.value}
                    onChange={(e) => updateFormField(field.id, e.target.value)}
                    className={cn('h-9', field.value && 'border-success/50 bg-success/5')}
                  />
                )}
                {field.type === 'select' && (
                  <Select value={field.value} onValueChange={(value) => updateFormField(field.id, value)}>
                    <SelectTrigger className={cn('h-9', field.value && 'border-success/50 bg-success/5')}>
                      <SelectValue placeholder={`Select ${field.label.toLowerCase()}`} />
                    </SelectTrigger>
                    <SelectContent>
                      {field.options?.map((option) => (
                        <SelectItem key={option} value={option}>
                          {option}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
                {field.type === 'textarea' && (
                  <Textarea
                    value={field.value}
                    onChange={(e) => updateFormField(field.id, e.target.value)}
                    placeholder={`Enter ${field.label.toLowerCase()}`}
                    rows={2}
                    className={cn(field.value && 'border-success/50 bg-success/5')}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="p-3 border-t border-pane-border bg-pane-header/30 flex justify-between">
          <Button variant="outline" size="sm" onClick={() => toast({ title: 'Draft saved' })}>
            Save Draft
          </Button>
          <Button size="sm" onClick={() => toast({ title: 'Form submitted successfully!', description: 'The application has been sent for review.' })}>
            Submit
          </Button>
        </div>
      </div>
    );
  };

  return (
    <div className="h-full w-full flex flex-col border-l border-pane-border bg-background">
      <div className="pane-header border-b border-pane-border">
        <div className="flex items-center gap-2">
          <ClipboardList className="w-4 h-4 text-primary" />
          <span>Application Form</span>
        </div>
      </div>
      {viewMode === 'metadata' ? renderMetadataView() : renderFormView()}
    </div>
  );
}
