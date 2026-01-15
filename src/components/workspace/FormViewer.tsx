import { useApp } from '@/contexts/AppContext';
import { ClipboardList, Sparkles, Database, Tag, Check, X, FileCode, Copy, Send, Loader2, Edit3 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/hooks/use-toast';
import { Badge } from '@/components/ui/badge';
import { SuggestedValue, FormField } from '@/types/case';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { FormModificationResponse, SHACLNodeShape, validateValue } from '@/types/shacl';
import SubmitCaseDialog from './SubmitCaseDialog';

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
  const { selectedDocument, formFields, updateFormField, currentCase, viewMode, isAdminMode, formSuggestions, acceptSuggestion, rejectSuggestion, setFormFields } = useApp();
  const { t } = useTranslation();

  // S5-001: Natural language form modification state
  const [showModifyDialog, setShowModifyDialog] = useState(false);
  const [modifyCommand, setModifyCommand] = useState('');
  const [isModifying, setIsModifying] = useState(false);
  const [commandHistory, setCommandHistory] = useState<string[]>([]);

  // S5-001: SHACL visualization state
  const [showShaclDialog, setShowShaclDialog] = useState(false);
  const [currentShaclShape, setCurrentShaclShape] = useState<SHACLNodeShape | null>(null);

  // S5-001: Validation state
  const [fieldValidationErrors, setFieldValidationErrors] = useState<Record<string, string>>({});

  // Case submission dialog state
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);

  // S5-001: Form modification handler
  const handleModifyForm = async () => {
    if (!modifyCommand.trim()) {
      toast({
        title: 'Empty command',
        description: 'Please enter a modification command.',
        variant: 'destructive',
      });
      return;
    }

    setIsModifying(true);

    try {
      const response = await fetch('/api/admin/modify-form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          command: modifyCommand,
          currentFields: formFields,
          caseId: currentCase.id,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail?.detail || 'Failed to modify form');
      }

      const data: FormModificationResponse = await response.json();

      // Update form fields with new fields
      setFormFields(data.fields as FormField[]);

      // Update SHACL shape
      setCurrentShaclShape(data.shaclShape);

      // Add to command history
      setCommandHistory(prev => [modifyCommand, ...prev].slice(0, 10));

      // Show success message
      toast({
        title: 'Form modified',
        description: data.modifications.join(', '),
      });

      // Clear command and close dialog
      setModifyCommand('');
      setShowModifyDialog(false);

    } catch (error: any) {
      toast({
        title: 'Modification failed',
        description: error.message || 'An error occurred',
        variant: 'destructive',
      });
    } finally {
      setIsModifying(false);
    }
  };

  // S5-001: SHACL visualization handler
  const handleViewShacl = async () => {
    // If we don't have a current shape, generate it
    if (!currentShaclShape) {
      try {
        const response = await fetch('/api/admin/modify-form', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            command: 'show current shape',
            currentFields: formFields,
            caseId: currentCase.id,
          }),
        });

        if (response.ok) {
          const data: FormModificationResponse = await response.json();
          setCurrentShaclShape(data.shaclShape);
        }
      } catch (error) {
        // If generation fails, create a simple shape
        setCurrentShaclShape({
          '@context': {
            sh: 'http://www.w3.org/ns/shacl#',
            schema: 'http://schema.org/',
            xsd: 'http://www.w3.org/2001/XMLSchema#',
          },
          '@type': 'sh:NodeShape',
          'sh:targetClass': 'schema:Thing',
          'sh:name': `${currentCase.name} Form`,
          'sh:property': formFields.map(f => f.shaclMetadata).filter(Boolean),
        } as SHACLNodeShape);
      }
    }
    setShowShaclDialog(true);
  };

  // S5-001: Copy SHACL to clipboard
  const handleCopyShacl = () => {
    if (currentShaclShape) {
      navigator.clipboard.writeText(JSON.stringify(currentShaclShape, null, 2));
      toast({
        title: 'Copied to clipboard',
        description: 'SHACL shape copied successfully',
      });
    }
  };

  // S5-001: Client-side validation function
  const validateFieldWithSHACL = (field: FormField, value: string) => {
    // Check required fields first (basic validation)
    if (field.required && (!value || value.trim() === '')) {
      const errorMsg = `${field.label} is required`;
      setFieldValidationErrors(prev => ({
        ...prev,
        [field.id]: errorMsg,
      }));
      return { isValid: false, errorMessage: errorMsg };
    }

    // If field has SHACL metadata, use SHACL validation
    if (field.shaclMetadata) {
      const result = validateValue(field.shaclMetadata, value);

      if (!result.isValid && result.errorMessage) {
        setFieldValidationErrors(prev => ({
          ...prev,
          [field.id]: result.errorMessage || 'Invalid value',
        }));
      } else {
        setFieldValidationErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors[field.id];
          return newErrors;
        });
      }

      return result;
    }

    // If no SHACL metadata and value exists, it's valid
    setFieldValidationErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[field.id];
      return newErrors;
    });

    return { isValid: true };
  };

  // S5-001: Validate all fields on form submission
  const handleFormSubmit = () => {
    // Open submit dialog instead of directly submitting
    setShowSubmitDialog(true);
  };

  // Actual form submission after validation dialog
  const handleConfirmedSubmit = () => {
    const errors: Record<string, string> = {};
    let isFormValid = true;

    // Validate all fields
    formFields.forEach(field => {
      const value = field.value || '';
      const result = validateFieldWithSHACL(field, value);

      if (!result.isValid) {
        isFormValid = false;
        errors[field.id] = result.errorMessage || 'Invalid value';
      }
    });

    // Update all errors at once
    setFieldValidationErrors(errors);

    if (!isFormValid) {
      toast({
        title: t('forms.validationFailed'),
        description: t('forms.fixErrors'),
        variant: 'destructive',
      });
      return;
    }

    // If validation passes, submit the form
    toast({
      title: t('forms.formSubmitted'),
      description: t('forms.sentForReview')
    });
  };

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
            <div className="flex items-center gap-2">
              <div>
                <h3 className="font-semibold text-foreground text-sm">{currentCase.name}</h3>
                <p className="text-xs text-muted-foreground">{currentCase.id}</p>
              </div>
              {/* S5-001: Admin mode buttons */}
              {isAdminMode && (
                <div className="flex items-center gap-1 ml-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2"
                    onClick={() => setShowModifyDialog(true)}
                    title="Modify form with natural language"
                  >
                    <Edit3 className="w-3.5 h-3.5 mr-1" />
                    <span className="text-xs">Modify</span>
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2"
                    onClick={handleViewShacl}
                    title="View SHACL shape"
                  >
                    <FileCode className="w-3.5 h-3.5" />
                  </Button>
                </div>
              )}
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
                    onBlur={(e) => validateFieldWithSHACL(field, e.target.value)}
                    placeholder={`Enter ${field.label.toLowerCase()}`}
                    className={cn('h-9', field.value && 'border-success/50 bg-success/5', fieldValidationErrors[field.id] && 'border-destructive')}
                  />
                )}
                {field.type === 'date' && (
                  <Input
                    type="date"
                    value={field.value}
                    onChange={(e) => updateFormField(field.id, e.target.value)}
                    onBlur={(e) => validateFieldWithSHACL(field, e.target.value)}
                    className={cn('h-9', field.value && 'border-success/50 bg-success/5', fieldValidationErrors[field.id] && 'border-destructive')}
                  />
                )}
                {field.type === 'select' && (
                  <Select value={field.value} onValueChange={(value) => { updateFormField(field.id, value); validateFieldWithSHACL(field, value); }}>
                    <SelectTrigger className={cn('h-9', field.value && 'border-success/50 bg-success/5', fieldValidationErrors[field.id] && 'border-destructive')}>
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
                    onBlur={(e) => validateFieldWithSHACL(field, e.target.value)}
                    placeholder={`Enter ${field.label.toLowerCase()}`}
                    rows={2}
                    className={cn(field.value && 'border-success/50 bg-success/5', fieldValidationErrors[field.id] && 'border-destructive')}
                  />
                )}
                {/* S5-001: Display validation error */}
                {fieldValidationErrors[field.id] && (
                  <p className="text-xs text-destructive mt-1">{fieldValidationErrors[field.id]}</p>
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
          <Button size="sm" onClick={handleFormSubmit}>
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

      {/* S5-001: Natural Language Form Modification Dialog */}
      <Dialog open={showModifyDialog} onOpenChange={setShowModifyDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Modify Form with Natural Language</DialogTitle>
            <DialogDescription>
              Describe your form modification in natural language. Examples: "Add an email field for contact email", "Remove the phone number field", "Add dropdown for marital status with options single, married, divorced"
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Command</label>
              <Textarea
                value={modifyCommand}
                onChange={(e) => setModifyCommand(e.target.value)}
                placeholder="e.g., Add an email field for contact email"
                rows={3}
                className="resize-none"
                disabled={isModifying}
              />
            </div>

            {commandHistory.length > 0 && (
              <div>
                <label className="text-sm font-medium mb-2 block">Recent Commands</label>
                <div className="space-y-1">
                  {commandHistory.slice(0, 5).map((cmd, idx) => (
                    <button
                      key={idx}
                      onClick={() => setModifyCommand(cmd)}
                      className="text-xs text-muted-foreground hover:text-foreground block w-full text-left px-2 py-1 rounded hover:bg-accent transition-colors"
                    >
                      {cmd}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowModifyDialog(false)} disabled={isModifying}>
              Cancel
            </Button>
            <Button onClick={handleModifyForm} disabled={isModifying || !modifyCommand.trim()}>
              {isModifying ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Apply
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* S5-001: SHACL Shape Visualization Dialog */}
      <Dialog open={showShaclDialog} onOpenChange={setShowShaclDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>SHACL Shape - {currentCase.name}</DialogTitle>
            <DialogDescription>
              JSON-LD representation of the form's SHACL shape with semantic validation
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <div className="relative">
              <pre className="bg-muted p-4 rounded-lg overflow-auto max-h-[50vh] text-xs font-mono">
                <code>{JSON.stringify(currentShaclShape, null, 2)}</code>
              </pre>
              <Button
                variant="ghost"
                size="sm"
                className="absolute top-2 right-2"
                onClick={handleCopyShacl}
              >
                <Copy className="w-4 h-4 mr-1" />
                Copy
              </Button>
            </div>
          </div>

          <DialogFooter>
            <Button onClick={() => setShowShaclDialog(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Case Submission Validation Dialog */}
      <SubmitCaseDialog
        open={showSubmitDialog}
        onOpenChange={setShowSubmitDialog}
        onSubmit={handleConfirmedSubmit}
      />
    </div>
  );
}
