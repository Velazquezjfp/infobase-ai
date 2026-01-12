import { useState } from 'react';
import { useApp } from '@/contexts/AppContext';
import {
  X, FolderTree, FileType, Zap, FileText, Tags,
  Plus, Trash2, GripVertical, Save, ChevronDown, ChevronRight,
  Sparkles, Loader2, AlertCircle, FileCode, Copy
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { generateField, validatePrompt, suggestFieldType, AdminApiError } from '@/lib/adminApi';
import { SHACLNodeShape } from '@/types/shacl';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { toast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface FolderTemplate {
  id: string;
  name: string;
  mandatory: boolean;
  children: FolderTemplate[];
}

interface DocumentType {
  id: string;
  name: string;
  mandatory: boolean;
  allowedFormats: string[];
  targetFolder: string;
}

interface MacroConfig {
  id: string;
  name: string;
  trigger: 'upload' | 'manual';
  action: string;
  enabled: boolean;
}

interface MetadataField {
  id: string;
  name: string;
  type: 'text' | 'date' | 'select' | 'number';
  required: boolean;
  options?: string[];
}

export default function AdminConfigPanel() {
  const { setIsAdminMode, formFields, setFormFields } = useApp();
  const { t } = useTranslation();
  
  // Folder Templates State
  const [folderTemplates, setFolderTemplates] = useState<FolderTemplate[]>([
    { id: '1', name: 'Personal Data', mandatory: true, children: [] },
    { id: '2', name: 'Certificates', mandatory: true, children: [] },
    { id: '3', name: 'Integration Course Documents', mandatory: true, children: [] },
    { id: '4', name: 'Applications & Forms', mandatory: true, children: [] },
    { id: '5', name: 'Additional Evidence', mandatory: false, children: [] },
  ]);

  // Document Types State
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([
    { id: '1', name: 'Birth Certificate', mandatory: true, allowedFormats: ['pdf', 'jpg', 'png'], targetFolder: 'Personal Data' },
    { id: '2', name: 'Language Certificate', mandatory: true, allowedFormats: ['pdf'], targetFolder: 'Certificates' },
    { id: '3', name: 'Course Completion', mandatory: false, allowedFormats: ['pdf', 'docx'], targetFolder: 'Integration Course Documents' },
    { id: '4', name: 'Application Form', mandatory: true, allowedFormats: ['pdf', 'xml'], targetFolder: 'Applications & Forms' },
  ]);

  // Macros State
  const [macros, setMacros] = useState<MacroConfig[]>([
    { id: '1', name: 'Convert to PDF', trigger: 'upload', action: 'convert_pdf', enabled: true },
    { id: '2', name: 'Translate to German', trigger: 'upload', action: 'translate_de', enabled: true },
    { id: '3', name: 'Extract Metadata', trigger: 'upload', action: 'extract_metadata', enabled: true },
    { id: '4', name: 'Anonymize PII', trigger: 'manual', action: 'anonymize', enabled: false },
  ]);

  // Metadata Fields State
  const [metadataFields, setMetadataFields] = useState<MetadataField[]>([
    { id: '1', name: 'Document Date', type: 'date', required: true },
    { id: '2', name: 'Source', type: 'select', required: true, options: ['Upload', 'Email', 'Scan', 'External System'] },
    { id: '3', name: 'Classification', type: 'select', required: false, options: ['Public', 'Internal', 'Confidential'] },
    { id: '4', name: 'Notes', type: 'text', required: false },
  ]);

  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['1', '2']));

  // AI Field Generation State
  const [aiPrompt, setAiPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [suggestedType, setSuggestedType] = useState<string | null>(null);

  // S5-001: SHACL Visualization State
  const [showShaclDialog, setShowShaclDialog] = useState(false);
  const [currentShaclShape, setCurrentShaclShape] = useState<SHACLNodeShape | null>(null);

  const toggleFolderExpand = (id: string) => {
    setExpandedFolders(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const addFolder = () => {
    const newFolder: FolderTemplate = {
      id: `folder-${Date.now()}`,
      name: 'New Folder',
      mandatory: false,
      children: [],
    };
    setFolderTemplates([...folderTemplates, newFolder]);
  };

  const removeFolder = (id: string) => {
    setFolderTemplates(folderTemplates.filter(f => f.id !== id));
  };

  const updateFolder = (id: string, updates: Partial<FolderTemplate>) => {
    setFolderTemplates(folderTemplates.map(f => 
      f.id === id ? { ...f, ...updates } : f
    ));
  };

  const addDocumentType = () => {
    const newType: DocumentType = {
      id: `doctype-${Date.now()}`,
      name: 'New Document Type',
      mandatory: false,
      allowedFormats: ['pdf'],
      targetFolder: 'Additional Evidence',
    };
    setDocumentTypes([...documentTypes, newType]);
  };

  const removeDocumentType = (id: string) => {
    setDocumentTypes(documentTypes.filter(d => d.id !== id));
  };

  const updateDocumentType = (id: string, updates: Partial<DocumentType>) => {
    setDocumentTypes(documentTypes.map(d =>
      d.id === id ? { ...d, ...updates } : d
    ));
  };

  const addMacro = () => {
    const newMacro: MacroConfig = {
      id: `macro-${Date.now()}`,
      name: 'New Macro',
      trigger: 'manual',
      action: 'custom',
      enabled: false,
    };
    setMacros([...macros, newMacro]);
  };

  const removeMacro = (id: string) => {
    setMacros(macros.filter(m => m.id !== id));
  };

  const updateMacro = (id: string, updates: Partial<MacroConfig>) => {
    setMacros(macros.map(m =>
      m.id === id ? { ...m, ...updates } : m
    ));
  };

  const addMetadataField = () => {
    const newField: MetadataField = {
      id: `meta-${Date.now()}`,
      name: 'New Field',
      type: 'text',
      required: false,
    };
    setMetadataFields([...metadataFields, newField]);
  };

  const removeMetadataField = (id: string) => {
    setMetadataFields(metadataFields.filter(f => f.id !== id));
  };

  const updateMetadataField = (id: string, updates: Partial<MetadataField>) => {
    setMetadataFields(metadataFields.map(f =>
      f.id === id ? { ...f, ...updates } : f
    ));
  };

  const addFormField = () => {
    const newField = {
      id: `field-${Date.now()}`,
      label: 'New Field',
      value: '',
      type: 'text' as const,
      required: false,
    };
    setFormFields([...formFields, newField]);
  };

  // AI Field Generation Handlers
  const handleAiPromptChange = (value: string) => {
    setAiPrompt(value);
    setGenerateError(null);
    const suggested = suggestFieldType(value);
    setSuggestedType(suggested);
  };

  const handleGenerateField = async () => {
    const validation = validatePrompt(aiPrompt);
    if (!validation.isValid) {
      setGenerateError(validation.error || 'Invalid prompt');
      return;
    }

    setIsGenerating(true);
    setGenerateError(null);

    try {
      const generatedField = await generateField(aiPrompt);
      setFormFields([...formFields, generatedField]);
      setAiPrompt('');
      setSuggestedType(null);
    } catch (error) {
      if (error instanceof AdminApiError) {
        setGenerateError(error.message);
        if (error.validationErrors) {
          setGenerateError(`${error.message}: ${error.validationErrors.join(', ')}`);
        }
      } else {
        setGenerateError('Failed to generate field. Please try again.');
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const removeFormField = (id: string) => {
    setFormFields(formFields.filter(f => f.id !== id));
  };

  // S5-001: SHACL visualization handler
  const handleViewShacl = () => {
    // Generate SHACL shape from current fields if not already available
    if (!currentShaclShape && formFields.length > 0) {
      setCurrentShaclShape({
        '@context': {
          sh: 'http://www.w3.org/ns/shacl#',
          schema: 'http://schema.org/',
          xsd: 'http://www.w3.org/2001/XMLSchema#',
        },
        '@type': 'sh:NodeShape',
        'sh:targetClass': 'schema:Thing',
        'sh:name': 'Admin Form Configuration',
        'sh:property': formFields.map(f => f.shaclMetadata).filter(Boolean) as any[],
      });
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

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-card border border-border rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-muted/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-foreground">{t('admin.adminConfiguration')}</h2>
              <p className="text-sm text-muted-foreground">{t('admin.configDescription')}</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={() => setIsAdminMode(false)}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          <Tabs defaultValue="folders" className="w-full">
            <TabsList className="grid w-full grid-cols-5 mb-4">
              <TabsTrigger value="folders" className="text-xs sm:text-sm">
                <FolderTree className="w-4 h-4 mr-1.5 hidden sm:inline" />
                {t('admin.folders')}
              </TabsTrigger>
              <TabsTrigger value="doctypes" className="text-xs sm:text-sm">
                <FileType className="w-4 h-4 mr-1.5 hidden sm:inline" />
                {t('admin.docTypes')}
              </TabsTrigger>
              <TabsTrigger value="macros" className="text-xs sm:text-sm">
                <Zap className="w-4 h-4 mr-1.5 hidden sm:inline" />
                {t('admin.macros')}
              </TabsTrigger>
              <TabsTrigger value="forms" className="text-xs sm:text-sm">
                <FileText className="w-4 h-4 mr-1.5 hidden sm:inline" />
                {t('admin.forms')}
              </TabsTrigger>
              <TabsTrigger value="metadata" className="text-xs sm:text-sm">
                <Tags className="w-4 h-4 mr-1.5 hidden sm:inline" />
                {t('admin.metadata')}
              </TabsTrigger>
            </TabsList>

            {/* Folder Templates Tab */}
            <TabsContent value="folders" className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">{t('admin.folderTemplateStructure')}</CardTitle>
                  <CardDescription>{t('admin.defineFolderHierarchy')}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  {folderTemplates.map((folder) => (
                    <div
                      key={folder.id}
                      className="flex items-center gap-2 p-2 rounded-md border border-border bg-background group"
                    >
                      <GripVertical className="w-4 h-4 text-muted-foreground cursor-grab" />
                      <button 
                        onClick={() => toggleFolderExpand(folder.id)}
                        className="p-0.5"
                      >
                        {expandedFolders.has(folder.id) ? (
                          <ChevronDown className="w-4 h-4 text-muted-foreground" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-muted-foreground" />
                        )}
                      </button>
                      <FolderTree className="w-4 h-4 text-primary" />
                      <Input
                        value={folder.name}
                        onChange={(e) => updateFolder(folder.id, { name: e.target.value })}
                        className="flex-1 h-8"
                      />
                      <div className="flex items-center gap-2">
                        <Label className="text-xs text-muted-foreground">{t('admin.required')}</Label>
                        <Switch
                          checked={folder.mandatory}
                          onCheckedChange={(checked) => updateFolder(folder.id, { mandatory: checked })}
                        />
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => removeFolder(folder.id)}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addFolder} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    {t('admin.addFolder')}
                  </Button>
                </CardContent>
              </Card>

              {/* YAML Preview */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">{t('admin.templatePreviewYAML')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-3 rounded-md text-xs font-mono overflow-auto max-h-40">
{`folders:
${folderTemplates.map(f => `  - name: "${f.name}"
    mandatory: ${f.mandatory}
    children: []`).join('\n')}`}
                  </pre>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Document Types Tab */}
            <TabsContent value="doctypes" className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Document Type Definitions</CardTitle>
                  <CardDescription>Configure mandatory document types and their properties</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {documentTypes.map((docType) => (
                    <div
                      key={docType.id}
                      className="p-3 rounded-md border border-border bg-background space-y-3"
                    >
                      <div className="flex items-center gap-2">
                        <FileType className="w-4 h-4 text-primary" />
                        <Input
                          value={docType.name}
                          onChange={(e) => updateDocumentType(docType.id, { name: e.target.value })}
                          className="flex-1 h-8"
                        />
                        <div className="flex items-center gap-2">
                          <Badge variant={docType.mandatory ? "default" : "secondary"}>
                            {docType.mandatory ? 'Required' : 'Optional'}
                          </Badge>
                          <Switch
                            checked={docType.mandatory}
                            onCheckedChange={(checked) => updateDocumentType(docType.id, { mandatory: checked })}
                          />
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => removeDocumentType(docType.id)}
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                      <div className="flex gap-4 pl-6">
                        <div className="flex-1">
                          <Label className="text-xs text-muted-foreground">Allowed Formats</Label>
                          <Input
                            value={docType.allowedFormats.join(', ')}
                            onChange={(e) => updateDocumentType(docType.id, { 
                              allowedFormats: e.target.value.split(',').map(s => s.trim())
                            })}
                            placeholder="pdf, jpg, png"
                            className="h-8 mt-1"
                          />
                        </div>
                        <div className="flex-1">
                          <Label className="text-xs text-muted-foreground">Target Folder</Label>
                          <Select
                            value={docType.targetFolder}
                            onValueChange={(value) => updateDocumentType(docType.id, { targetFolder: value })}
                          >
                            <SelectTrigger className="h-8 mt-1">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {folderTemplates.map(f => (
                                <SelectItem key={f.id} value={f.name}>{f.name}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addDocumentType} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Document Type
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Macros Tab */}
            <TabsContent value="macros" className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Automation Macros</CardTitle>
                  <CardDescription>Configure automatic actions on document upload</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {macros.map((macro) => (
                    <div
                      key={macro.id}
                      className={cn(
                        "p-3 rounded-md border bg-background space-y-3",
                        macro.enabled ? "border-primary/50" : "border-border"
                      )}
                    >
                      <div className="flex items-center gap-2">
                        <Zap className={cn("w-4 h-4", macro.enabled ? "text-primary" : "text-muted-foreground")} />
                        <Input
                          value={macro.name}
                          onChange={(e) => updateMacro(macro.id, { name: e.target.value })}
                          className="flex-1 h-8"
                        />
                        <div className="flex items-center gap-2">
                          <Label className="text-xs text-muted-foreground">Enabled</Label>
                          <Switch
                            checked={macro.enabled}
                            onCheckedChange={(checked) => updateMacro(macro.id, { enabled: checked })}
                          />
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => removeMacro(macro.id)}
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                      <div className="flex gap-4 pl-6">
                        <div className="w-40">
                          <Label className="text-xs text-muted-foreground">Trigger</Label>
                          <Select
                            value={macro.trigger}
                            onValueChange={(value: 'upload' | 'manual') => updateMacro(macro.id, { trigger: value })}
                          >
                            <SelectTrigger className="h-8 mt-1">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="upload">On Upload</SelectItem>
                              <SelectItem value="manual">Manual</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="flex-1">
                          <Label className="text-xs text-muted-foreground">Action</Label>
                          <Select
                            value={macro.action}
                            onValueChange={(value) => updateMacro(macro.id, { action: value })}
                          >
                            <SelectTrigger className="h-8 mt-1">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="convert_pdf">Convert to PDF</SelectItem>
                              <SelectItem value="translate_de">Translate to German</SelectItem>
                              <SelectItem value="extract_metadata">Extract Metadata</SelectItem>
                              <SelectItem value="anonymize">Anonymize PII</SelectItem>
                              <SelectItem value="ocr">Run OCR</SelectItem>
                              <SelectItem value="validate">Validate Document</SelectItem>
                              <SelectItem value="custom">Custom Script</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addMacro} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Macro
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Form Definitions Tab */}
            <TabsContent value="forms" className="space-y-4">
              {/* AI Field Generation Card */}
              <Card className="border-primary/30 bg-primary/5">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-primary" />
                    AI Field Generator
                  </CardTitle>
                  <CardDescription>
                    Describe the field you need in natural language
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex gap-2">
                    <div className="flex-1 space-y-1">
                      <Textarea
                        placeholder='e.g., "Add a dropdown for marital status with options single, married, divorced"'
                        value={aiPrompt}
                        onChange={(e) => handleAiPromptChange(e.target.value)}
                        className="min-h-[60px] resize-none"
                        disabled={isGenerating}
                      />
                      {suggestedType && (
                        <p className="text-xs text-muted-foreground">
                          Detected type: <Badge variant="secondary" className="text-xs">{suggestedType}</Badge>
                        </p>
                      )}
                    </div>
                    <div className="flex flex-col gap-2">
                      <Button
                        onClick={handleGenerateField}
                        disabled={isGenerating || !aiPrompt.trim()}
                        className="flex-1"
                      >
                        {isGenerating ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            {t('admin.generating')}
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4 mr-2" />
                            {t('admin.generate')}
                          </>
                        )}
                      </Button>
                      {/* S5-001: View SHACL button */}
                      <Button
                        variant="outline"
                        onClick={handleViewShacl}
                        disabled={formFields.length === 0}
                        title="View SHACL Shape"
                        size="sm"
                      >
                        <FileCode className="w-4 h-4 mr-1" />
                        View SHACL
                      </Button>
                    </div>
                  </div>
                  {generateError && (
                    <div className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 p-2 rounded-md">
                      <AlertCircle className="w-4 h-4 flex-shrink-0" />
                      <span>{generateError}</span>
                    </div>
                  )}
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p className="font-medium">Example prompts:</p>
                    <ul className="list-disc list-inside space-y-0.5 pl-1">
                      <li>"Add a required text field for passport number"</li>
                      <li>"Create a date field for visa expiry date"</li>
                      <li>"Add dropdown for education level with options high school, bachelor, master, phd"</li>
                      <li>"I need a textarea for additional notes"</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>

              {/* Existing Form Fields Card */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Form Field Definitions</CardTitle>
                  <CardDescription>Configure the form fields for case applications</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  {formFields.map((field) => (
                    <div
                      key={field.id}
                      className={cn(
                        "flex items-center gap-2 p-2 rounded-md border bg-background group",
                        field.shaclMetadata ? "border-primary/30" : "border-border"
                      )}
                    >
                      <GripVertical className="w-4 h-4 text-muted-foreground cursor-grab" />
                      {field.shaclMetadata && (
                        <Sparkles className="w-3 h-3 text-primary flex-shrink-0" title="AI-generated field with SHACL metadata" />
                      )}
                      <Input
                        value={field.label}
                        onChange={(e) => {
                          setFormFields(formFields.map(f =>
                            f.id === field.id ? { ...f, label: e.target.value } : f
                          ));
                        }}
                        className="flex-1 h-8"
                      />
                      <Select
                        value={field.type}
                        onValueChange={(value: 'text' | 'textarea' | 'select' | 'date') => {
                          setFormFields(formFields.map(f =>
                            f.id === field.id ? { ...f, type: value } : f
                          ));
                        }}
                      >
                        <SelectTrigger className="w-28 h-8">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="text">Text</SelectItem>
                          <SelectItem value="textarea">Textarea</SelectItem>
                          <SelectItem value="select">Select</SelectItem>
                          <SelectItem value="date">Date</SelectItem>
                        </SelectContent>
                      </Select>
                      <div className="flex items-center gap-2">
                        <Label className="text-xs text-muted-foreground">Required</Label>
                        <Switch
                          checked={field.required}
                          onCheckedChange={(checked) => {
                            setFormFields(formFields.map(f =>
                              f.id === field.id ? { ...f, required: checked } : f
                            ));
                          }}
                        />
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => removeFormField(field.id)}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addFormField} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Field Manually
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Metadata Fields Tab */}
            <TabsContent value="metadata" className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Metadata Field Definitions</CardTitle>
                  <CardDescription>Configure custom metadata fields for documents</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {metadataFields.map((field) => (
                    <div
                      key={field.id}
                      className="p-3 rounded-md border border-border bg-background space-y-3"
                    >
                      <div className="flex items-center gap-2">
                        <Tags className="w-4 h-4 text-primary" />
                        <Input
                          value={field.name}
                          onChange={(e) => updateMetadataField(field.id, { name: e.target.value })}
                          className="flex-1 h-8"
                        />
                        <Select
                          value={field.type}
                          onValueChange={(value: 'text' | 'date' | 'select' | 'number') => 
                            updateMetadataField(field.id, { type: value })
                          }
                        >
                          <SelectTrigger className="w-28 h-8">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="text">Text</SelectItem>
                            <SelectItem value="date">Date</SelectItem>
                            <SelectItem value="select">Select</SelectItem>
                            <SelectItem value="number">Number</SelectItem>
                          </SelectContent>
                        </Select>
                        <div className="flex items-center gap-2">
                          <Label className="text-xs text-muted-foreground">Required</Label>
                          <Switch
                            checked={field.required}
                            onCheckedChange={(checked) => updateMetadataField(field.id, { required: checked })}
                          />
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => removeMetadataField(field.id)}
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                      {field.type === 'select' && (
                        <div className="pl-6">
                          <Label className="text-xs text-muted-foreground">Options (comma-separated)</Label>
                          <Input
                            value={field.options?.join(', ') || ''}
                            onChange={(e) => updateMetadataField(field.id, {
                              options: e.target.value.split(',').map(s => s.trim())
                            })}
                            placeholder="Option 1, Option 2, Option 3"
                            className="h-8 mt-1"
                          />
                        </div>
                      )}
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addMetadataField} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Metadata Field
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-border bg-muted/30">
          <p className="text-xs text-muted-foreground">
            {t('admin.changesApplied')}
          </p>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setIsAdminMode(false)}>
              {t('admin.cancel')}
            </Button>
            <Button onClick={() => setIsAdminMode(false)}>
              <Save className="w-4 h-4 mr-2" />
              {t('admin.saveAndClose')}
            </Button>
          </div>
        </div>
      </div>

      {/* S5-001: SHACL Shape Visualization Dialog */}
      <Dialog open={showShaclDialog} onOpenChange={setShowShaclDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>SHACL Shape - Form Configuration</DialogTitle>
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
    </div>
  );
}
