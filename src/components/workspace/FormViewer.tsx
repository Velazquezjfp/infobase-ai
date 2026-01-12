import { useApp } from '@/contexts/AppContext';
import { ClipboardList, Sparkles, Database, Tag, Check, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/hooks/use-toast';
import { Badge } from '@/components/ui/badge';
import { SuggestedValue } from '@/types/case';
import { useTranslation } from 'react-i18next';

interface FormViewerProps {
  showMetadata?: boolean;
}

/**
 * S5-002: Inline suggestion component with accept/reject actions
 * Displays under form fields when AI suggests a different value
 */
function SuggestedValueInline({
  fieldId,
  suggestion,
  onAccept,
  onReject,
  t
}: {
  fieldId: string;
  suggestion: SuggestedValue;
  onAccept: () => void;
  onReject: () => void;
  t: (key: string) => string;
}) {
  const confidencePercent = Math.round(suggestion.confidence * 100);
  const isLowConfidence = suggestion.confidence < 0.5;

  // Color coding based on confidence
  const colorClasses = isLowConfidence
    ? 'bg-yellow-50 border-yellow-200'
    : 'bg-blue-50 border-blue-200';

  const textColorClasses = isLowConfidence
    ? 'text-yellow-700'
    : 'text-blue-700';

  return (
    <div className={cn('mt-1.5 flex items-center gap-2 text-sm px-3 py-1.5 rounded-md border', colorClasses)}>
      <Sparkles className={cn('w-3.5 h-3.5 flex-shrink-0', textColorClasses)} />
      <div className="flex-1 flex items-center gap-2">
        <span className={textColorClasses}>
          {t('forms.suggested')}: <span className="font-medium">{suggestion.value}</span>
        </span>
        <span className={cn('text-xs', isLowConfidence ? 'text-yellow-600' : 'text-blue-500')}>
          ({confidencePercent}% {t('forms.confidence')})
        </span>
      </div>
      <button
        onClick={onAccept}
        className="p-1 rounded hover:bg-green-100 text-green-600 hover:text-green-700 transition-colors"
        title={t('forms.acceptSuggestion')}
      >
        <Check size={16} />
      </button>
      <button
        onClick={onReject}
        className="p-1 rounded hover:bg-red-100 text-red-600 hover:text-red-700 transition-colors"
        title={t('forms.rejectSuggestion')}
      >
        <X size={16} />
      </button>
    </div>
  );
}

export default function FormViewer({ showMetadata = false }: FormViewerProps) {
  const { selectedDocument, formFields, updateFormField, currentCase, viewMode, isAdminMode, formSuggestions, acceptSuggestion, rejectSuggestion } = useApp();
  const { t } = useTranslation();

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
            <h3 className="font-semibold text-foreground">{t('metadata.title')}</h3>
          </div>
          <p className="text-sm text-muted-foreground">{selectedDocument?.name || t('documents.noDocumentSelected')}</p>
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
            <h4 className="text-sm font-medium text-foreground mb-2">{t('metadata.addCustomField')}</h4>
            <div className="flex gap-2">
              <Input placeholder={t('metadata.fieldName')} className="flex-1 h-8 text-sm" />
              <Input placeholder={t('metadata.value')} className="flex-1 h-8 text-sm" />
              <Button size="sm" className="h-8" onClick={() => toast({ title: t('metadata.fieldAdded') })}>{t('metadata.add')}</Button>
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
                <p className="text-xs text-muted-foreground">{t('forms.filled')}</p>
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
                {t('forms.aiHelper')}
              </p>
            </div>

            {formFields.map((field) => (
              <div key={field.id} className="space-y-1.5">
                <label className="block text-sm font-medium text-foreground">
                  {t(`formFields.${field.label}`, field.label)}
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
                {/* S5-002: Display inline suggestion if available */}
                {formSuggestions[field.id] && (
                  <SuggestedValueInline
                    fieldId={field.id}
                    suggestion={formSuggestions[field.id]}
                    onAccept={() => acceptSuggestion(field.id)}
                    onReject={() => rejectSuggestion(field.id)}
                    t={t}
                  />
                )}
                {/* S2-003: Display SHACL metadata in admin mode */}
                {isAdminMode && field.shaclMetadata && (
                  <div className="flex items-center gap-1.5 mt-1">
                    <Tag className="w-3 h-3 text-muted-foreground" />
                    <Badge variant="outline" className="text-xs font-mono px-1.5 py-0">
                      {field.shaclMetadata['sh:path']}
                    </Badge>
                    <Badge variant="secondary" className="text-xs font-mono px-1.5 py-0">
                      {field.shaclMetadata['sh:datatype']}
                    </Badge>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="p-3 border-t border-pane-border bg-pane-header/30 flex justify-between">
          <Button variant="outline" size="sm" onClick={() => toast({ title: t('forms.draftSaved') })}>
            {t('forms.saveDraft')}
          </Button>
          <Button size="sm" onClick={() => toast({ title: t('forms.formSubmitted'), description: t('forms.sentForReview') })}>
            {t('forms.submit')}
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
